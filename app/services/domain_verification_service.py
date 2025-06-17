from email.mime.text import MIMEText
import logging
import smtplib
from uuid import UUID
from datetime import datetime

import dns.resolver

from app.core.exceptions import ValidationException
from app.repositories.email_verification_repository import EmailVerificationRepository
from app.core.config import settings

logger = logging.getLogger(__name__)

class DomainVerificationService:
    """Service for verifying domain ownership through DNS and SMTP."""
    
    def __init__(self):
        self.email_verifier = EmailVerificationRepository()
        
    async def verify_domain(self, domain: str, company_id: UUID, method: str = "dns") -> bool:
        """Verify domain ownership using specified method."""
        try:
            if method == "dns":
                return await self._verify_dns(domain, company_id)
            elif method == "smtp":
                return await self._verify_smtp(domain, company_id)
            else:
                raise ValidationException("Invalid verification method")
        except Exception as e:
            logger.error(f"Domain verification failed: {str(e)}")
            raise ValidationException("Domain verification failed")
    
    async def _verify_dns(self, domain: str, company_id: UUID) -> bool:
        """Verify domain ownership through DNS records."""
        try:
            # Generate verification token
            verification_token = f"skillsync-verify={company_id}"
            
            # Check for TXT record
            try:
                txt_records = dns.resolver.resolve(domain, "TXT")
                for record in txt_records:
                    if verification_token in str(record):
                        await self._update_verification_status(domain, company_id)
                        return True
            except dns.resolver.NXDOMAIN:
                pass
            except dns.resolver.NoAnswer:
                pass
            
            # Check for CNAME record
            try:
                cname_records = dns.resolver.resolve(domain, "CNAME")
                for record in cname_records:
                    if "skillsync-verify" in str(record):
                        await self._update_verification_status(domain, company_id)
                        return True
            except dns.resolver.NXDOMAIN:
                pass
            except dns.resolver.NoAnswer:
                pass
            
            return False
        
        except Exception as e:
            logger.error(f"DNS verification failed: {str(e)}")
            return False
        
    async def _verify_smtp(self, domain: str, company_id: UUID) -> bool:
        """Verify domain ownership through SMTP."""
        try:
            try:
                mx_records = dns.resolver.resolve(domain, "MX")
                if not mx_records:
                    return False
                
                # Try to connect to the first MX server
                mx_host = str(mx_records[0].exchange)
                
                # Create test email
                test_email = f"verify-{company_id}@{domain}"
                message = MIMEText("This is a verification email")
                message["Subject"] = "Domain Verification"
                message["From"] = settings.SMTP_FROM
                message["To"] = test_email
                
                # Try to send email
                with smtplib.SMTP(mx_host, 25) as server:
                    server.starttls()
                    server.send_message(message)
                    
                await self._update_verification_status(domain, company_id)
                return True
                    
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                    return False
            except smtplib.SMTPException:
                return False
            
        except Exception as e:
            logger.error(f"SMTP verification failed: {str(e)}")
            return False
        
    async def _update_verification_status(self, domain: str, company_id: UUID) -> None:
        """Update domain verification status in database."""
        try:
            # Update domain verification status
            domain_data = {
                "domain": domain,
                "company_id": str(company_id),
                "verification_status": "verified",
                "verification_date": datetime.utcnow().isoformat(),
                "last_verified_at": datetime.utcnow().isoformat()
            }
            
            await self.email_verifier.verify_company_domain(domain, company_id)
            
        except Exception as e:
            logger.error(f"Failed to update verification status: {str(e)}")
            raise
        
    async def get_verification_instructions(self, domain: str, company_id: UUID, method: str = "dns") -> dict:
        """Get instructions for domain verification."""
        if method == "dns":
            return {
                "method": "dns",
                "instructions": [
                    "Add a TXT record to your domain's DNS settings:",
                    f"Name: @ or {domain}",
                    f"Value: skillsync-verify={company_id}",
                    "OR",
                    "Add a CNAME record:",
                    f"Name: verify.{domain}",
                    "Value: skillsync-verify.skillsync.com"
                ]
            }
        elif method == "smtp":
            return {
                "method": "smtp",
                "instructions": [
                    "Ensure your domain has valid MX records",
                    "Make sure your mail server is properly configured",
                    "Allow incoming emails from our verification system"
                ]
            }
        else:
            raise ValidationException("Invalid verification method")
        