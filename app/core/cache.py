from redis import Redis
from app.core.config import settings
from typing import Any, Optional
import pickle
from functools import wraps

class Cache:
    def __init__(self):
        self.redis = Redis.from_url(settings.REDIS_URL)
    
    def get(self, key: str) -> Optional[Any]:
        data = self.redis.get(key)
        if data:
            return pickle.loads(data)
        return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        return self.redis.setex(
            key,
            expire,
            pickle.dumps(value)
        )
    
    def delete(self, key: str) -> bool:
        return bool(self.redis.delete(key))

def get_cache() -> Cache:
    return Cache() 