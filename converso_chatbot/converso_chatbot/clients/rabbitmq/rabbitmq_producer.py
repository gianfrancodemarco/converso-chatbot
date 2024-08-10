import logging
from typing import Annotated

import pika

from .constants import RABBITMQ_HOST, RABBITMQ_PASSWORD, RABBITMQ_PORT, RABBITMQ_USER

logger = logging.getLogger(__name__)


class RabbitMQProducer:

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

        self.connection = None
        self.channel = None

    def connect(self):
        connection_params = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            credentials=pika.PlainCredentials(self.user, self.password)
        )
        self.connection = pika.BlockingConnection(connection_params)
        self.channel = self.connection.channel()

    def publish(
        self,
        queue: str,
        message: str
    ):
        # TODO: we are connecting at every message, there must be a better
        # way...
        self.connect()
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.basic_publish(
            exchange='', routing_key=queue, body=message)


def get_rabbitmq_producer():
    client = RabbitMQProducer(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        user=RABBITMQ_USER,
        password=RABBITMQ_PASSWORD
    )
    return client


RabbitMQProducerDep = None
try:
    from fastapi import Depends
    RabbitMQProducerDep = Annotated[RabbitMQProducer, Depends(
        get_rabbitmq_producer)]
except ImportError:
    pass
