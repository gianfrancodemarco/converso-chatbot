import asyncio
import json
import logging
from typing import Coroutine

import aio_pika

from .constants import (RABBITMQ_HOST, RABBITMQ_PASSWORD, RABBITMQ_PORT,
                        RABBITMQ_USER)

logger = logging.getLogger(__name__)


class RabbitMQConsumer:
    def __init__(
        self,
        on_message_callback: Coroutine[dict, None, None],
        queue_name: str
    ):
        self.queue_name = queue_name
        self.on_message_callback = on_message_callback
        self.connection = None
        self.lock = asyncio.Lock()

    async def on_message(self, message):
        async with message.process():
            async with self.lock:
                body = json.loads(message.body.decode())
                logging.debug(f" [x] Received {body}")
                await self.on_message_callback(body)
                # Your processing logic here
                # For example, you can call an async function:
                # await process_message(body)

    async def setup_consumer(self):
        self.connection = await aio_pika.connect_robust(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            login=RABBITMQ_USER,
            password=RABBITMQ_PASSWORD,
            reconnect_interval=15
        )
        channel = await self.connection.channel()
        queue = await channel.declare_queue(self.queue_name, durable=True)
        await queue.consume(self.on_message)

    async def run_consumer(self):
        await self.setup_consumer()


def get_rabbitmq_consumer(
    on_message_callback: Coroutine[dict, None, None],
    queue_name: str
):
    return RabbitMQConsumer(
        on_message_callback=on_message_callback,
        queue_name=queue_name
    )
