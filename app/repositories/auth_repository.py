from typing import Any, Dict, List, Optional
from uuid import UUID
import logging
from app.infrastructure.supabase_client import SupabaseClient
from app.repositories.base import BaseRepository
from app.domain.auth.models import AuthMethod, UserInDB
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

class AuthRepository(BaseRepository[UserInDB]):
    """Repository for handling user authentication data."""
    
    def __init__(self):
        self.client = SupabaseClient.get_instance()
        self.users_table = "users"
        self.auth_method_table = "auth_methods"
        self.social_accounts_table = "social_accounts"
    
    async def create(self, user: UserInDB) -> UserInDB:
        """Create a new user in the database."""
        try:
            data = user.model_dump()
            result = self.client.table(self.users_table).insert(data).execute()
            return UserInDB(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise AppException("Failed to create user.")
    
    async def get_by_id(self, id: UUID) -> Optional[UserInDB]:
        """Retrieve a user by their ID"""
        try:
            result = self.client.table(self.users_table)\
                .select('*')\
                .eq('id', str(id))\
                .execute()
            return UserInDB(**result.data[0]) if result.data else None
        except Exception as e:
            logger.error(f"Failed to get user by ID: {str(e)}")
            raise AppException("Failed to get user by ID.")
    
    async def get_all(self) -> List[UserInDB]:
        """Retrieve all users"""
        try:
            result = self.client.table(self.users_table).select('*').execute()
            return [UserInDB(**user) for user in result.data]
        except Exception as e:
            logger.error(f"Failed to get all users: {str(e)}")
            raise AppException("Failed to get all users.")
    
    async def update(self, id: UUID, user: UserInDB) -> Optional[UserInDB]:
        """Update an existing user"""
        try:
            data = user.model_dump()
            result = self.client.table(self.users_table)\
                .update(data)\
                .eq('id', str(id))\
                .execute()
            return UserInDB(**result.data[0]) if result.data else None
        except Exception as e:
            logger.error(f"Failed to update user: {str(e)}")
            raise AppException("Failed to update user.")
    
    async def delete(self, id: UUID) -> bool:
        """Delete an existing user by their ID"""
        try:
            result = self.client.table(self.users_table)\
                .delete()\
                .eq('id', str(id))\
                .execute()
            return bool(result.data)
        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            raise AppException("Failed to delete user.")
    
    async def get_by_email(self, email: str) -> Optional[UserInDB]:
        """Retrieve a user by their email"""
        try:
            result = self.client.table(self.users_table)\
                .select('*')\
                .eq('email', email)\
                .execute()
            return UserInDB(**result.data[0]) if result.data else None
        except Exception as e:
            logger.error(f"Failed to get user by email: {str(e)}")
            raise AppException("Failed to get user by email.")
    
    async def get_by_phone(self, phone: str) -> Optional[UserInDB]:
        """Retrieve a user by their phone number"""
        try:
            result = self.client.table(self.users_table)\
                .select('*')\
                .eq('phone', phone)\
                .execute()
            return UserInDB(**result.data[0]) if result.data else None
        except Exception as e:
            logger.error(f"Failed to get user by phone: {str(e)}")
            raise AppException("Failed to get user by phone.")
    
    async def get_by_social_id(self, provider: str, social_id: str) -> Optional[UserInDB]:
        """Retrieve a user by their social account"""
        try:
            social_result = self.client.table(self.social_accounts_table)\
                .select("user_id")\
                .eq("provider", provider)\
                .eq("social_id", social_id)\
                .execute()
            
            if not social_result.data:
                return None
            
            user_result = self.client.table(self.users_table)\
                .select('*')\
                .eq("id", social_result.data[0]["user_id"])\
                .execute()
            
            return UserInDB(**user_result.data[0]) if user_result.data else None
        except Exception as e:
            logger.error(f"Failed to get user by social account: {str(e)}")
            raise AppException("Failed to get user by social account.")
    
    async def create_auth_method(self, auth_method: AuthMethod) -> AuthMethod:
        """Create a new auth method for a user"""
        try:
            data = auth_method.model_dump()
            result = self.client.table(self.auth_method_table).insert(data).execute()
            return AuthMethod(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to create auth method: {str(e)}")
            raise AppException("Failed to create auth method in DB.")
    
    async def get_auth_methods(self, user_id: UUID) -> List[AuthMethod]:
        """Retrieve all authentication methods for a user"""
        try:
            result = self.client.table(self.auth_method_table)\
                .select('*')\
                .eq('user_id', str(user_id))\
                .execute()
            return [AuthMethod(**auth_method) for auth_method in result.data]
        except Exception as e:
            logger.error(f"Failed to get auth methods: {str(e)}")
            raise AppException("Failed to get auth methods.")
    
    async def link_social_accounts(self, user_id: UUID, provider: str, social_id: str, email: Optional[str] = None) -> None:
        """Link a social account to a user"""
        try:
            social_data = {
                "user_id": str(user_id),
                "provider": provider,
                "social_id": social_id,
                "email": email
            }
            
            self.client.table(self.social_accounts_table).insert(social_data).execute()
        except Exception as e:
            logger.error(f"Failed to link social account: {str(e)}")
            raise AppException("Failed to link social account.")
    
    async def verify_password(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user password using Supabase Auth."""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not response.user:
                return None
            
            user = await self.get_by_email(email)
            return user
        except Exception as e:
            logger.error(f"Failed to verify password: {str(e)}")
            raise AppException("Failed to verify password.")
    
    async def verify_otp(self, phone: str, otp: str) -> Optional[Dict[str, Any]]:
        """Verify OTP for phone login using Supabase Auth."""
        try:
            response = self.client.auth.verify_otp({
                "phone": phone,
                "token": otp
            })
            
            if not response.user:
                return None
            
            user = await self.get_by_phone(phone)
            return user
        except Exception as e:
            logger.error(f"Failed to verify OTP: {str(e)}")
            raise AppException("Failed to verify OTP.")
    
    async def send_otp(self, phone: str) -> None:
        """Send OTP using Supabase Auth."""
        try:
            self.client.auth.sign_in_with_otp({
                "phone": phone
            })
        except Exception as e:
            logger.error(f"Failed to send OTP: {str(e)}")
            raise AppException("Failed to send OTP.")
    
    async def reset_password(self, email: str) -> None:
        """Send password reset email using Supabase Auth."""
        try:
            self.client.auth.reset_password_for_email(email)
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            raise AppException("Failed to send password reset email.")
    
"""
1. Class Structure:
    . Implements BaseRepository with UserInDB type
    . Uses Supabase client for database operations
    . Manages both users and auth_methods tables
    
2. Core Methods (inherited from BaseRepository):
    . create: Creates new user
    . get_by_id: Gets user by UUID
    . get_all: Lists all users
    . update: Updates user info
    . delete: Removes user
    
3. Auth-Specific Methods:
    . get_by_email: Finds user by email
    . get_by_phone: Finds user by phone
    . create_auth_method: Adds auth method
    . get_auth_methods: Lists user's auth methods
    
4. The BaseRepository class defines the common CRUD operations that all repositories should implement.
   The auth-specific methods like get_by_email, get_by_phone, etc., are specific to the AuthRepository 
   and don't belong in the base class.
   This follows the Interface Segregation Principle - we don't want to force all repositories to implement methods 
   that are only relevant to authentication.
"""