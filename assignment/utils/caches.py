import os
import redis


BASE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
PROD_REDIS_URL = BASE_REDIS_URL + '/0'
TEST_REDIS_URL = BASE_REDIS_URL + '/1'

class RedisConnection(object):

    @staticmethod
    def get_connection(url):
        return redis.StrictRedis.from_url(url)

class RedisStore(object):
    
    ttl = None
    check_exists = False

    def __init__(self, connection=None):
        self.connection = connection or RedisConnection.get_connection(PROD_REDIS_URL)

    def get(self, key):
        return self.connection.get(key)

    def set(self, key, val):
        kwargs = {'nx': self.check_exists}
        if self.ttl:
            kwargs['ex'] = self.ttl

        return self.connection.set(key, val, **kwargs)

    def setincr(self, key, amount):
        p = self.connection.pipeline()

        kwargs = {'nx': self.check_exists}
        if self.ttl:
            kwargs['ex'] = self.ttl

        p.set(key, 0, **kwargs)
        p.incr(key, amount)
        p.execute()

    def incr(self, key, amount):
       return self.connection.incr(key, amount)

    def exists(self, key):
        return self.connection.exists(key)
