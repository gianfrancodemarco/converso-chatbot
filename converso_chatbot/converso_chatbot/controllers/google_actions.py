import logging
import pickle

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from converso_chatbot.clients import (CreateCalendarEventPayload,
                              GetCalendarEventsPayload, GoogleClient,
                              RedisClientDep)
from converso_chatbot.constants import RedisKeys

logger = logging.getLogger(__name__)
google_actions_router = APIRouter(prefix="/google")


@google_actions_router.post("/{chat_id}/calendar")
def create_calendar_event(
    chat_id: str,
    data: CreateCalendarEventPayload,
    redis_client: RedisClientDep
):

    credentials = redis_client.hget(
        chat_id,
        RedisKeys.GOOGLE_CREDENTIALS.value
    )
    if not credentials:
        raise ValueError("No Google credentials found. User must login first.")
    credentials = pickle.loads(credentials)

    # TODO: This can be obtained with dependency injection
    # The endpoint should set the credentials in the object
    google_client = GoogleClient(credentials=credentials)

    google_client.create_calendar_event(
        data
    )

    return JSONResponse(
        status_code=200,
        content={"message": "Event created"}
    )


@google_actions_router.get("/{chat_id}/calendar")
def create_calendar_event(
    chat_id: str,
    data: GetCalendarEventsPayload,
    redis_client: RedisClientDep
):

    credentials = redis_client.hget(
        chat_id,
        RedisKeys.GOOGLE_CREDENTIALS.value
    )
    if not credentials:
        raise ValueError("No Google credentials found. User must login first.")
    credentials = pickle.loads(credentials)

    # TODO: This can be obtained with dependency injection
    # The endpoint should set the credentials in the object
    google_client = GoogleClient(credentials=credentials)

    events = google_client.get_calendar_events(data)

    return JSONResponse(
        status_code=200,
        content={"content": events}
    )
