import redis

"""
Redis caching will be used for the following services:
1. Earthquake view (Map)
2. Earthquake AI Summary (Gemini API)
"""

# initialize the redis object using localhost
redis_client = redis.Redis(host="localhost", port=6379, db=0)

# create Cache class 
class Cache:
    # for initializing a Cache object, accept key and time to live (expiry)
    def __init__(self, key, ttl=60):
        self.key = key
        self.ttl = ttl
        self.redis_client = redis_client

    # function for retrieving the data using key
    def get(self):
        # retrieve data using key
        data = self.redis_client.get(self.key)

        # if data exists, return its decoded version
        # note: no need for proper encrypting/decrypting for now since all is public data
        if data is not None:
            return data.decode('utf-8')
        
        # else, return None
        return None
    
    # function for setting/storing the data in the cache
    def set(self, data):
        # store the data using the key and data 
        self.redis_client.set(self.key, data)
        # set the cache duration using ttl value
        self.redis_client.expire(self.key, self.ttl)

