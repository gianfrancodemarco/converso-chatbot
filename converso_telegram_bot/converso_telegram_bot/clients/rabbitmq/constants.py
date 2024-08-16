import os

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
RABBITMQ_PORT = os.environ.get('RABBITMQ_PORT', 5672)
RABBITMQ_PASSWORD = os.environ.get('RABBITMQ_PASSWORD')
RABBITMQ_USER = 'user'

# Convert port to int if it is a string (Due to the fact that Kubernetes
# automatically populates some env variables from the services)
if isinstance(RABBITMQ_PORT, str) and ':' in RABBITMQ_PORT:
    RABBITMQ_PORT = int(RABBITMQ_PORT.split(':')[-1])
