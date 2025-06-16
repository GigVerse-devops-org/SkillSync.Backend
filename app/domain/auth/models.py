from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model with common attributes."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    first_name: str
    last_name: str
    country: str
    user_type: str = Field(..., description="Type of user: 'job_seeker' or 'client'")
    is_active: bool = True
    is_verified: bool = False
    work_status: Optional[str] = None
    company_id: Optional[UUID] = None
    
class UserCreate(UserBase):
    """Model for creating a new user."""
    password: Optional[str] = None # Optional for social login
    
class UserInDB(UserBase):
    """Model for user as stored in database."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
class AuthMethod(BaseModel):
    """Model for authentication methods."""
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    auth_type: str = Field(..., description="Type of auth: 'email', 'phone', 'google', etc.")
    auth_provider: Optional[str] = None
    auth_id: str # Email, phone number, or social ID
    is_primary: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = None
    password_hash: Optional[str] = None
    email_verification_token: Optional[str] = None
    phone_otp: Optional[str] = None
    
class Token(BaseModel):
    """Model for authentication tokens."""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    
"""
1. UserBase Model:
    . Common attributes for all users
    . email and phone are optional (user might use either)
    . user_type to distinguish between job seekers and clients
    . is_active and is_verified flags for account status
    
2. UserCreate Model:
    . Extends UserBase
    . Adds password field (optional for social login)
    . Used when creating new users
    
3. UserInDB Model:
    . Extends UserBase
    . Adds database-specific fields:
    . id: UUID for unique identification
    . created_at and updated_at timestamps
    
4. AuthMethod Model:
    . Tracks different authentication methods for a user
    . Supports multiple auth methods (email, phone, social)
    . Stores provider-specific information
    . Tracks usage with last_used
"""