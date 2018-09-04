import redis


PROD_DB=0
TEST_DB=1

class RedisConnection(redis.StrictRedis):

    def __init__(self, host='localhost', port=6379, db=PROD_DB):
        super().__init__(host=host, port=port, db=db)

class RedisStore(object):
    
    ttl = None
    check_exists = False

    def __init__(self, connection=None):
        self.connection = connection or RedisConnection()

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
