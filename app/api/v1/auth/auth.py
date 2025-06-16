from fastapi import APIRouter, HTTPException

from app.api.v1.auth.schemas import (
    LoginRequest, 
    PasswordResetRequest, 
    RegistrationRequest, 
    UserResponse
)
from app.domain.auth.models import UserCreate
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()

@router.post("/register", response_model=UserResponse)
async def register_user(request: RegistrationRequest):
    """Register a new user."""
    try:
        user_data = UserCreate(
            email=request.email,
            phone=request.phone,
            first_name=request.first_name,
            last_name=request.last_name,
            country=request.country,
            user_type=request.user_type,
            work_status=request.work_status,
            password=request.password
        )
        
        company_data = None
        if request.user_type == "client":
            company_data = {
                "company_name": request.company_name,
                "registration_number": request.registration_number,
                "country": request.company_country
            }
        
        user = await auth_service.register_user(
            user_data=user_data,
            registration_type=request.registration_type,
            company_data=company_data,
            auth_provider=request.auth_provider,
            social_id=request.social_id
        )
        
        return UserResponse(**user.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=UserResponse)
async def login_user(request: LoginRequest):
    """Login user with various methods."""
    try:
        user = await auth_service.login_user(
            email=request.email,
            password=request.password,
            phone=request.phone,
            otp=request.otp,
            auth_provider=request.auth_provider,
            social_id=request.social_id
        )
        
        return UserResponse(**user.model_dump())
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/send-otp")
async def send_otp(phone: str):
    """Send OTP for phone verification."""
    try:
        await auth_service.send_otp(phone)
        return {"message": "OTP sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset-password")
async def reset_password(request: PasswordResetRequest):
    """Send password reset email."""
    try:
        await auth_service.reset_password(request.email)
        return {"message": "Password reset email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))