from datetime import datetime, timedelta
import json
import logging
from uuid import UUID, uuid4

from app.core.exceptions import ValidationException
from app.infrastructure.redis_client import RedisClient
from app.infrastructure.supabase_client import SupabaseClient
from app.infrastructure.email_client import EmailClient
from app.core.config import settings


logger = logging.getLogger(__name__)

class EmailVerificationRepository:
    """Repository for handling email verification and domain validation."""
    def __init__(self):
        self.redis_client = RedisClient.get_instance()
        self.supabase_client = SupabaseClient.get_instance()
        self.email_client = EmailClient.get_instance()
        
    async def validate_company_email(self, email: str) -> bool:
        """Validate if email belongs to a verified company domain."""
        try:
            domain = email.split("@")[1]
            
            # Check Redis cache first
            cached_domain = self.redis_client.get(f"domain:{domain}")
            if cached_domain:
                domain_data = json.loads(cached_domain)
                return domain_data.get("is_company_domain", False) and domain_data.get("verification_status") == "verified"
            
            # If not in cache, check database
            response = await self.supabase_client.table("email_domains")\
                .select('*')\
                .eq("domain", domain)\
                .execute()
                
            if not response.data:
                return False
            
            domain_data = response.data[0]
            
            # Cache the data
            self.redis_client.set(
                f"domain:{domain}",
                settings.EMAIL_VERIFICATION_EXPIRY,
                json.dumps(domain_data)
            )
            
            return domain_data.get("is_company_domain", False) and domain_data.get("verification_status") == "verified"
        
        except Exception as e:
            logger.error(f"Failed to validate company email: {str(e)}")
            raise ValidationException("Failed to validate company email")
        
    async def create_verification(self, email: str, user_id: UUID) -> str:
        """Create email verification record and send verification email."""
        try:
            # Generate verification token
            token = str(uuid4())
            expires_at = datetime.utcnow() + timedelta(seconds=settings.EMAIL_VERIFICATION_EXPIRY)
            
            # Store verification data in Redis
            data = {
                "email": email,
                "user_id": str(user_id),
                "verified": False,
                "expires_at": expires_at.isoformat()
            }
            
            self.redis_client.setex(
                f"email_verification:{token}",
                settings.EMAIL_VERIFICATION_EXPIRY,
                json.dumps(data)
            )
            
            # Send verification email
            await self.email_client.send_verification_email(email, token)
            
            return token
        
        except Exception as e:
            logger.error(f"Failed to create email verification: {str(e)}")
            raise ValidationException("Failed to create email verification")
        
    async def verify_email(self, token: str) -> bool:
        """Verify email using token."""
        try:
            # Get verification data from Redis
            verification_data = self.redis_client.get(f"email_verification:{token}")
            if not verification_data:
                raise ValidationException("Invalid or expired verification token")
            
            data = json.loads(verification_data)
            
            # Check if already verified
            if data.get("verified", False):
                return True
            
            # Check if expired
            expires_at = datetime.fromisoformat(data["expires_at"])
            if datetime.utcnow() > expires_at:
                raise ValidationException("Verification token has expired")
            
            # Update verification status
            data["verified"] = True
            self.redis_client.setex(
                f"email_verification:{token}",
                settings.EMAIL_VERIFICATION_EXPIRY,
                json.dumps(data)
            )
            
            # Update user verification status in database
            await self.supabase_client.table("users").update({
                "is_verified": True
            }).eq("id", data["user_id"]).execute()
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to verify email: {str(e)}")
            raise ValidationException("Failed to verify email")
        
    async def verify_company_domain(self, domain: str, company_id: UUID) -> None:
        """Verify company domain ownership."""
        try:
            # Check if domain already exists
            response = await self.supabase_client.table("email_domains")\
                .select('*')\
                .eq("domain", domain)\
                .execute()
                
            domain_data = {
                "domain": domain,
                "company_id": str(company_id),
                "is_company_domain": True,
                "verification_status": "verified",
                "verification_date": datetime.utcnow().isoformat(),
                "last_verified_at": datetime.utcnow().isoformat()
            }
            
            if response.data:
                await self.supabase_client.table("email_domains")\
                    .update(domain_data)\
                    .eq("domain", domain)\
                    .execute()
            else:
                await self.supabase_client.table("email_domains")\
                    .insert(domain_data)\
                    .execute()
                    
            # Cache the result
            self.redis_client.setex(
                f"domain:{domain}",
                settings.EMAIL_VERIFICATION_EXPIRY,
                json.dumps(domain_data)
            )
            
        except Exception as e:
            logger.error(f"Failed to verify company domain: {str(e)}")
            raise ValidationException("Failed to verify company domain") 