"""
Clients to interact with external services
Dep are FastAPI dependencies that can be injected into FastAPI routes
"""

from .google import (CreateCalendarEventPayload, GetCalendarEventsPayload,
                     GetEmailsPayload, GoogleClient, SendEmailPayload)
from .google_search import GoogleSearchClient, GoogleSearchClientPayload
from .rabbitmq import (RabbitMQConsumer, RabbitMQProducer, RabbitMQProducerDep,
                       get_rabbitmq_consumer, get_rabbitmq_producer)
from .redis import RedisClientDep, get_redis_client
