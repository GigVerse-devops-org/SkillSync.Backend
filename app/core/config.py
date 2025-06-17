from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SkillSync Backend"
    
    # Security
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # OpenAI
    OPENAI_API_KEY: str
    
    # Logtail
    LOGTAIL_SOURCE_TOKEN: str
    LOGTAIL_INGESTING_HOST: str
    
    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # Email Verification Settings
    EMAIL_VERIFICATION_EXPIRY: int = 24 * 60 * 60 # 24 hours in seconds
    
    # SMTP Settings
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM: str = "noreply@skillsync.com"
    SMTP_FROM_NAME: str = "SkillSync"
    SMTP_PORT: int = 587
    SMTP_SERVER: str = "smtp.gmail.com"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings() 