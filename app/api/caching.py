import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)

class Cache:
    def __init__(self, key, ttl=60):
        self.key = key
        self.ttl = ttl
        self.redis_client = redis_client

    def get(self):
        data = self.redis_client.get(self.key)

        if data is not None:
            return data.decode('utf-8')
        
        return None
    
    def set(self, data):
        self.redis_client.set(self.key, data)
        self.redis_client.expire(self.key, self.ttl)

