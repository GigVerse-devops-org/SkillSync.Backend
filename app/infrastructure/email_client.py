import logging
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailClient:
    """Client for handling email operations."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.config = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USERNAME,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.SMTP_FROM,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_SERVER,
            MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.fastmail = FastMail(self.config)
    
    async def send_verification_email(self, email: EmailStr, token: str) -> None:
        """Send email verification link."""
        try:
            verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
            
            message = MessageSchema(
                subject="Verify your email address",
                recipients=[email],
                body=f"""
                <html>
                    <body>
                        <h1>Welcome to SkillSync!</h1>
                        <p>Please verify your email address by clicking the link below:</p>
                        <p><a href="{verification_url}">Verify Email</a></p>
                        <p>This link will expire in 24 hours.</p>
                        <p>If you did not create an account, please ignore this email.</p>
                    </body>
                </html>
                """,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Verification email sent to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            raise
    
    async def send_password_reset_email(self, email: EmailStr, token: str) -> None:
        """Send password reset link."""
        try:
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
            
            message = MessageSchema(
                subject="Reset your password",
                recipients=[email],
                body=f"""
                <html>
                    <body>
                        <h1>Password Reset Request</h1>
                        <p>You have requested to reset your password. Click the link below to proceed:</p>
                        <p><a href="{reset_url}">Reset Password</a></p>
                        <p>This link will expire in 1 hour.</p>
                        <p>If you did not request a password reset, please ignore this email.</p>
                    </body>
                </html>
                """,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Password reset email sent to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send password reset email: {str(e)}")
            raise
    
    async def send_welcome_email(self, email: EmailStr, name: str) -> None:
        """Send welcome email after successful registration."""
        try:
            message = MessageSchema(
                subject="Welcome to SkillSync!",
                recipients=[email],
                body=f"""
                <html>
                    <body>
                        <h1>Welcome to SkillSync, {name}!</h1>
                        <p>Thank you for joining our platform. We're excited to have you on board!</p>
                        <p>Get started by:</p>
                        <ul>
                            <li>Completing your profile</li>
                            <li>Exploring available opportunities</li>
                            <li>Connecting with other professionals</li>
                        </ul>
                        <p>If you have any questions, feel free to reach out to our support team.</p>
                    </body>
                </html>
                """,
                subtype="html"
            )
            
            await self.fastmail.send_message(message)
            logger.info(f"Welcome email sent to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            raise 