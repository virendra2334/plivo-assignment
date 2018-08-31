import redis

class RedisConnection(redis.StrictRedis):

    def __init__(self, host='localhost', port=6379, db=0):
        super().__init__(host=host, port=port, db=db)


