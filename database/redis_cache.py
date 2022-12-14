import os

import redis

from logs import logger

redis_host = os.environ.get('REDIS_HOST')

try:

    pool_upload = redis.ConnectionPool(host=redis_host, port=6379, db=0)
    red_upload = redis.Redis(connection_pool=pool_upload)

    pool_transform = redis.ConnectionPool(host=redis_host, port=6379, db=1)
    red_transform = redis.Redis(connection_pool=pool_transform)

    pool_response = redis.ConnectionPool(host=redis_host, port=6379, db=2)
    red_response = redis.Redis(connection_pool=pool_response)

except Exception as e:
    logger.log("error", "[Server, Redis]: " + str(e), "none")
