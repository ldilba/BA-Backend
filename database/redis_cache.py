import os

import redis

redis_host = os.environ.get('REDIS_HOST')

pool_transform = redis.ConnectionPool(host=redis_host, port=6379, db=1)
red_transform = redis.Redis(connection_pool=pool_transform)

pool_response = redis.ConnectionPool(host=redis_host, port=6379, db=2)
red_response = redis.Redis(connection_pool=pool_response)


def set_session(app):
    app.secret_key = '|9vpN<gctB6fBvv5MqV5|XMAOE0Qu3'
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERMANENT'] = False

    pool_session = redis.ConnectionPool(host=redis_host, port=6379, db=0)
    app.config['SESSION_REDIS'] = redis.Redis(connection_pool=pool_session)
