import logging
from redis import StrictRedis

from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    _instance: StrictRedis = None
    
    @classmethod
    def get_instance(cls):
        """Create or get Redis client"""
        try:
            if not cls._instance:
                cls._instance = StrictRedis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                    decode_responses=True
                )
                return cls._instance
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {str(e)}")
            raise
        
    @classmethod
    def clear_instance(cls):
        """Reset the client instance (useful for testing)."""
        cls._instance = None