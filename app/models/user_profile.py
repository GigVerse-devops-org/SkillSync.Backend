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
    full_name: str = Field(..., description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    headline: Optional[str] = Field(None, description="Headline or current role")
    summary: Optional[str] = Field(None, description="Professional summary")
    location: Optional[str] = Field(None, description="Location (City, Country)")
    skills: List[Skill] = Field(default_factory=list, description="List of skills")
    experience: List[Experience] = Field(default_factory=list, description="Work Experience")
    education: List[Education] = Field(default_factory=list, description="Education history")
    certifications: List[Certification] = Field(default_factory=list, description="Certifications")
    social_links: List[SocialLink] = Field(default_factory=list, description="Social links")
    languages: List[Language] = Field(default_factory=list, description="Languages")
    profile_photo_url: Optional[HttpUrl] = Field(None, description="URL to profile photo")
    resume_file_url: Optional[HttpUrl] = Field(None, description="URL to uploaded resume")
    video_intro_url: Optional[HttpUrl] = Field(None, description="URL to video intro")