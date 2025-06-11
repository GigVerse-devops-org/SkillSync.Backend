from datetime import date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, HttpUrl

# --- Leaf models (smallest building blocks) ---

class Skill(BaseModel):
    name: str
    proficiency_level: Optional[int] = Field(None, ge=1, le=5) # 1-5 optional
    verified: Optional[bool] = False
    
class Experience(BaseModel):
    name: str
    company: str
    start_date: Optional[date]
    end_date: Optional[date]
    description: Optional[str]
    
class Education(BaseModel):
    degree: str
    institution: str
    start_date: Optional[date]
    end_date: Optional[date]
    description: Optional[str]
    
class Certification(BaseModel):
    name: str
    authority: Optional[str]
    year: Optional[int]
    credential_Url: Optional[HttpUrl]
    
class SocialLink(BaseModel):
    type: str
    url: HttpUrl
    
class Language(BaseModel):
    name: str
    proficiency: Optional[str] # E.g., "Basic", "Fluent"
    
# --- Main Profile Model ---
class UserProfile(BaseModel):
    full_name: str
    email: Optional[EmailStr]
    headline: Optional[str]
    summary: Optional[str]
    location: Optional[str]
    skills: List[Skill] = []
    experience: List[Experience] = []
    education: List[Experience] = []
    certifications: List[Certification] = []
    social_links: List[SocialLink] = []
    languages: List[Language] = []
    profile_photo_url: Optional[HttpUrl]
    resume_file_url: Optional[HttpUrl]
    video_intro_url: Optional[HttpUrl]
