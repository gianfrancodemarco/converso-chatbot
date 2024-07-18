"""
File containing endpoints and functions for Google login.
"""

import json
import logging
import pickle
import random
import string

from fastapi import APIRouter
from google_auth_oauthlib.flow import Flow
from starlette.exceptions import HTTPException

from converso.clients import RabbitMQProducerDep, RedisClientDep
from converso.constants import MessageQueues, MessageType, RedisKeys

logger = logging.getLogger(__name__)
google_login_router = APIRouter(prefix="/google")

GOOGLE_CLIENT_SECRET_PATH = "/client_secret.json"
REDIRECT_URI = "http://localhost:8000/google/callback"
SCOPES = ['https://www.googleapis.com/auth/calendar',
          'https://mail.google.com/']


def generate_state_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


def generate_authorization_url():

    state_token = generate_state_token()
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRET_PATH,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
        state=state_token)
    authorization_url, _ = flow.authorization_url(prompt='consent')
    return authorization_url, state_token


@google_login_router.post("/login/{chat_id}")
def login(
    chat_id: str,
    redis_client: RedisClientDep
):
    """
    Returns a URL to login to Google.
    """
    authorization_url, state_token = generate_authorization_url()

    # Store the state token in the user credentials mapping
    redis_client.hset(
        chat_id,
        RedisKeys.GOOGLE_STATE_TOKEN.value,
        state_token
    )

    # Also, set the state token as the key and the user ID as the value in the
    # mapping for lookup later
    redis_client.hset(
        RedisKeys.GOOGLE_STATE_TOKEN.value,
        state_token,
        chat_id
    )

    return {"content": authorization_url}

# Handle the callback on your existing web server


@google_login_router.get('/callback')
def callback(
    code: str,
    state: str,
    redis_client: RedisClientDep,
    rabbitmq_client: RabbitMQProducerDep
):
    """
    We store the state token 2 times:
    1. In a mapping of state tokens to user IDs
    2. In the object containing all of the user conversation data

    When we receive the callback, we first fetch the state token as the key of the mapping.
    If it doesn't exist, we return an error.
    If it does exist, we get the value, which is the user ID.

    We then fetch the state token from the user conversation data object.
    If it doesn't exist, we return an error.
    If it does exist, we compare the state tokens.
    If they match, the token is valid and we can proceed.

    This flow is a bit complicated and might be revised in the future.
    """

    authorization_code = code
    state_token = state

    # Verify that the state token is valid
    chat_id = redis_client.hget(
        RedisKeys.GOOGLE_STATE_TOKEN.value,
        state_token
    )

    if not chat_id:
        raise HTTPException(status_code=400, detail="Invalid state token.")

    chat_id = chat_id.decode("utf-8")

    # Get the stored user and compare the state tokens
    stored_conversation_google_state_token = redis_client.hget(
        chat_id,
        RedisKeys.GOOGLE_STATE_TOKEN.value
    )

    if not stored_conversation_google_state_token:
        raise HTTPException(status_code=400, detail="Invalid state token.")

    stored_conversation_google_state_token = stored_conversation_google_state_token.decode(
        "utf-8")

    if state_token != stored_conversation_google_state_token:
        raise HTTPException(status_code=400, detail="Invalid state token.")

    # Get user credentials
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRET_PATH,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI)

    # Horrendous hack to get around the fact that we can't use localhost as a
    # redirect URI...
    flow.fetch_token(authorization_response=REDIRECT_URI.replace(
        "http", "https") + f'?code={authorization_code}')

    # Save the obtained tokens securely
    credentials = flow.credentials
    redis_client.hset(
        chat_id,
        RedisKeys.GOOGLE_CREDENTIALS.value,
        pickle.dumps(credentials)
    )

    # Publish a message to the RabbitMQ queue
    rabbitmq_client.publish(
        queue=MessageQueues.converso_OUT.value,
        message=json.dumps({
            "type": MessageType.TEXT.value,
            "chat_id": chat_id,
            "content": "Successfully logged in to Google."
        })
    )

    return {"content": "Successfully logged in to Google."}
