from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.models.profile import UserProfile

router = APIRouter()

@router.post("/profile/build", response_model=UserProfile)
async def build_profile(
    file: UploadFile = File(None),
    profile_text: str = Form(None)
):
    # 1. Validate input: must have either file or profile text
    if not file or not profile_text:
        raise HTTPException(status_code=400, detail="Must provide either a resume file or profile text.")
    
    # 2. (Placeholder) Simulate extraction logic
    # In future, you'll add file reading, LLM, etc.
    dummy_profile = {
        "full_name": "Priya Sharma",
        "email": "priya@example.com",
        "headline": "Backend Developer",
        "summary": "10 years in SaaS, built scalable APIs...",
        "location": "Bangalore, India",
        "skills": [{"name": "Python", "proficiency": 5, "verified": False}],
        "experience": [],
        "education": [],
        "certifications": [],
        "social_links": [],
        "languages": [],
        "profile_photo_url": None,
        "resume_file_url": None,
        "video_intro_url": None
    }
    
    return dummy_profile