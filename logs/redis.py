import redis
from logs import settings


class RedisClient(object):
    def __init__(self):
        self.connection = redis.Redis(host=settings.REDIS_HOST,
                                            port=settings.REDIS_PORT,
                                            db=settings.REDIS_DB,
                                    )
        print(self.connection)

    def set(self,name,value):
        self.connection.set(name,value)

    def get(self,name):
        return self.connection.get(name)
