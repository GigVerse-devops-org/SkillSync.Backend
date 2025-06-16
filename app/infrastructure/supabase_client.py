import logging
from supabase import Client, create_client
from app.core.config import settings

logger = logging.getLogger(__name__)

class SupabaseClient:
    """Singleton class for supabase client"""
    _instance: Client = None
    
    @classmethod
    def get_instance(cls) -> Client:
        """Create or get supabase client"""
        try:
            if not cls._instance:
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_ANON_KEY
                )
            return cls._instance
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {str(e)}")
            raise
    
    @classmethod
    def clear_instance(cls) -> None:
        """Reset the client instance (useful for testing)."""
        cls._instance = None
        
"""
1. SupabaseClient Class:
    . Implements the Singleton pattern
    . Ensures only one Supabase client instance exists
    . Uses settings from our config
    
2. Methods:
    . get_instance: Creates or returns existing client
    . reset_instance: Useful for testing or reconnection
    
3. The @classmethod decorator is used here because:
    . It allows us to call the method without creating an instance of the class (e.g., SupabaseClient.get_instance())
    . It has access to the class itself through the cls parameter, which is needed to maintain the singleton instance
    . It's more appropriate than @staticmethod because we need to access the class variable _instance
"""