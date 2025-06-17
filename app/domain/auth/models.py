from datetime import date, datetime
from typing import Literal, Optional
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
    
class EmailDomain(BaseModel):
    """Model for email domain validation and verification."""
    id: UUID = Field(default_factory=uuid4)
    domain: str = Field(..., description="Email domain (e.g., company.com)")
    is_company_domain: bool = Field(default=False, description="Whether this is a company domain")
    verification_status: Literal["pending", "verified", "rejected"] = Field(
        default="pending",
        description="Domain verification status"
    )
    verification_method: Optional[Literal["dns", "smtp", "manual"]] = Field(
        default=None,
        description="Method used to verify the domain"
    )
    verification_date: Optional[date] = Field(
        default=None,
        description="When the domain was verified"
    )
    company_id: Optional[UUID] = Field(
        default=None,
        description="ID of the company this domain belongs to"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "domain": "company.com",
                "is_company_domain": True,
                "verification_status": "pending",
                "verification_method": "dns",
                "company_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
    
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