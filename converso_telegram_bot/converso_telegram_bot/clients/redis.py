import os
from typing import Annotated

import redis

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')


def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        password=REDIS_PASSWORD
    )


RedisClientDep = None
try:
    from fastapi import Depends
    RedisClientDep = Annotated[redis.Redis, Depends(get_redis_client)]
except ImportError:
    pass
