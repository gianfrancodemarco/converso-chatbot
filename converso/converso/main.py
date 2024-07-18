import asyncio
import logging

from fastapi import FastAPI

from converso.clients.rabbitmq import RabbitMQConsumer
from converso.constants import MessageQueues
from converso.controllers import (conversations_router, google_actions_router,
                                  google_login_router)
from converso.conversational_engine import process_message

# Add stream and file handlers to logger. Use basic config
# to avoid adding duplicate handlers when reloading server
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("langchain.log"),
        logging.StreamHandler()
    ]
)

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple API server using LangChain's Runnable interfaces",
)

app.include_router(conversations_router)
app.include_router(google_login_router)
app.include_router(google_actions_router)

asyncio.get_event_loop().create_task(RabbitMQConsumer(
    queue_name=MessageQueues.converso_IN.value,
    on_message_callback=process_message
).run_consumer())
