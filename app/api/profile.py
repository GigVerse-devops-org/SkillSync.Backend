from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.models.profile import UserProfile
from app.services.resume_extractor import extract_resume_text

router = APIRouter()

@router.post("/profile/build", response_model=UserProfile)
async def build_profile(
    file: UploadFile = File(None),
    profile_text: str = Form(None)
):
    # Validate input: must have either file or profile text
    if not file and not profile_text:
        raise HTTPException(status_code=400, detail="Must provide either a resume file or profile text.")
    
    # Extract text from file or use pasted text
    try:
        if file:
            text = await extract_resume_text(file)
        else:
            text = profile_text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Resume extraction error: {str(e)}")
    
    # For now, just return the raw extracted text
    return { "extracted_text": text }