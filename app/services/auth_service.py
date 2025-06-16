from datetime import datetime
from uuid import uuid4
from app.domain.auth.models import AuthMethod, UserCreate, UserInDB
from app.domain.company.models import Company
from app.repositories.auth_repository import AuthRepository
from app.repositories.company_repository import CompanyRepository
from app.core.exceptions import ValidationException, AppException
from app.utils.password_utils import hash_password, validate_password

class AuthService:
    def __init__(self):
        self.auth_repo = AuthRepository()
        self.company_repo = CompanyRepository()
    
    async def register_user(
        self, 
        user_data: UserCreate, 
        registration_type: str, 
        company_data: dict = None, 
        auth_provider: str = None, 
        social_id: str = None
    ) -> UserInDB:
        user_id = uuid4()
        now = datetime.utcnow()
        
        company_id = None
        if user_data.user_type.lower() == "client":
            if not company_data or not company_data.get("company_name"):
                raise ValidationException("Company information is required for client registration.")
            
            company = await self.company_repo.get_by_name(company_data["company_name"])
            if not company:
                company = Company(
                    company_name=company_data["company_name"],
                    registration_number=company_data["registration_number"],
                    country=company_data["country"]
                )
                company = await self.company_repo.create(company)
            
            company_id = company.id
        
        password_hash = None
        if registration_type == "email":
            if not user_data.password:
                raise ValidationException("Password is required for email registration.")
            
            if not validate_password(user_data.password):
                raise ValidationException("Password does not meet security requirements.")
            
            password_hash = hash_password(user_data.password)
        
        if registration_type not in ["email", "phone"]:
            if not social_id:
                raise ValidationException("Social registration requires social_id and auth_provider.")
        
        user = UserInDB(
            id=user_id,
            email=user_data.email,
            phone=user_data.phone,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            country=user_data.country,
            user_type=user_data.user_type,
            is_active=True,
            is_verified=False,
            work_status=user_data.work_status,
            company_id=company_id,
            created_at=now,
            updated_at=now
        )
        
        created_user = await self.auth_repo.create(user)
        
        auth_method = AuthMethod(
            id=user_id,
            auth_type=registration_type,
            auth_provider=auth_provider,
            auth_id=user_data.email if registration_type == "email" else (
                user_data.phone if registration_type == "phone" else social_id
            ),
            password_hash=password_hash,
            is_primary=True,
            created_at=now
        )
        await self.auth_repo.create_auth_method(auth_method)
        
        return created_user
    
    async def login_user(
        self,
        email: str = None,
        password: str = None,
        phone: str = None,
        otp: str = None,
        auth_provider: str = None,
        social_id: str = None
    ) -> UserInDB:
        """Login user with various methods."""
        try:
            user = None
            
            # Email/Password login
            if email and password:
                user = await self.auth_repo.verify_password(email, password)
            
            # Phone/OTP login
            elif phone and otp:
                user = await self.auth_repo.verify_otp(phone, otp)
            
            # Social login
            elif auth_provider and social_id:
                user = await self.auth_repo.get_by_social_id(auth_provider, social_id)
            
            if not user:
                raise ValidationException("Invalid credentials")
            
            return user
            
        except ValidationException:
            raise
        except Exception as e:
            raise AppException(f"Failed to login user: {str(e)}")
    
    async def send_otp(self, phone: str) -> None:
        """Send OTP for phone verification."""
        try:
            await self.auth_repo.send_otp(phone)
        except Exception as e:
            raise AppException(f"Failed to send OTP: {str(e)}")
    
    async def reset_password(self, email: str) -> None:
        """Send password reset email."""
        try:
            await self.auth_repo.reset_password(email)
        except Exception as e:
            raise AppException(f"Failed to send password reset email: {str(e)}")