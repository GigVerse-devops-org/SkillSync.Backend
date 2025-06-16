from datetime import datetime
from uuid import UUID
import phonenumbers
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal

class RegistrationRequest(BaseModel):
    user_type: Literal["job_seeker", "client"]
    registration_type: Literal["email", "phone", "google", "linkedin", "apple"]
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    country: str
    region: Optional[str] = "IN" # ISO country code, default to India
    work_status: Optional[Literal["experienced", "fresher"]] = None
    company_name: Optional[str] = None
    registration_number: Optional[str] = None
    company_country: Optional[str] = None
    social_id: Optional[str] = None
    auth_provider: Optional[str] = None
    
    @field_validator
    def validate_phone(cls, v, info):
        region = info.data.get("region", "IN")
        if cls.phone is not None:
            try:
                parsed = phonenumbers.parse(v, region)
                if not phonenumbers.is_valid_number_for_region(parsed, region):
                    raise ValueError(f"Invalid phone number for region {region}")
            except Exception:
                raise ValueError(f"Invalid phone number for region {region}")
        return v
    
class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    otp: Optional[str] = None
    auth_provider: Optional[str] = None
    social_id: Optional[str] = None
    
    @field_validator
    def validate_login_method(cls, v):
        if not any([v.email, v.phone, v.social_id]):
            raise ValueError("At least one login method must be provided")
        return v
    
class PasswordResetRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    @field_validator
    def validate_reset_method(cls, v):
        if not v.email and not v.phone:
            raise ValueError("Either email or phone must be provided")
        return v
    
class UserResponse(BaseModel):
    id: UUID
    email: Optional[EmailStr]
    first_name: str
    last_name: str
    country: str
    user_type: str
    is_active: bool
    is_verified: bool
    work_status: Optional[str]
    company_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime      
    
class PhoneVerificationRequest(BaseModel):
    phone: str
    
class VerificationResponse(BaseModel):
    success: bool
    message: str