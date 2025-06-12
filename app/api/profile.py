import logging
import os
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.models.user_profile import UserProfile
from app.services.profile_generator import ProfileGenerationError, generate_profile_llm
from app.services.resume_extractor import ResumeExtractionError, extract_resume_text
from app.core.settings import settings

router = APIRouter()
logger = logging.getLogger(__name__)

async def validate_file(file: Optional[UploadFile] = None) -> None:
    if not file:
        return
    
    extension = os.path.split(file.filename)[1].lower()
    if extension not in settings.ALLOWED_FILE_EXTENSIONS:
        logger.error(f"Unsupported file type: {extension}")
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed file types: {', '.join(settings.ALLOWED_FILE_EXTENSIONS)}"
        )
        
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        logger.error(f"Unsupported content type: {file.content_type}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content type. Allowed content types: {', '.join(settings.ALLOWED_MIME_TYPES)}"
        )
        
    file_size_mb: float = file.size / (1024 * 1024)
    if file_size_mb > settings.ALLOWED_FILE_SIZE_MB:
        logger.error(f"File size too large: {file_size_mb}MB.")
        raise HTTPException(
            status_code=400,
            detail=f"File size too large. Allowed file size: {settings.ALLOWED_FILE_SIZE_MB}MB"
        )

@router.post("/profile/build", response_model=UserProfile)
async def build_profile(
    file: UploadFile = File(None),
    profile_text: str = Form(None)
):
    logger.info("API request: '/profile/build' received.")
    
    # Validate input: must have either file or profile text
    if not file and not profile_text:
        logger.error("Must provide either a resume file or profile text")
        raise HTTPException(
            status_code=400, 
            detail="Must provide either a resume file or profile text."
        )
    
    if file:
        logger.info(f"Validating received file: {file.filename}")
        
    try:
        await validate_file(file)
        
        if file:
            logger.info(f"Processing uploaded file: {file.filename}")
            contents = await file.read()
            
            if len(contents) < 100:
                logger.error(f"File too small or empty.")
                raise HTTPException(
                    status_code=400, 
                    detail="Uploaded resume file is either incomplete or empty. Make sure to upload proper resume files.")
                
            logger.info("Extracting text from file...")
            extension = os.path.split(file.filename)[1].lower()
            resume_text: str = extract_resume_text(contents, extension)
        else:
            resume_text = profile_text
            
        logger.info("Generating profile from text...")
        user_profile = await generate_profile_llm(resume_text)
        logger.info("Profile generated successfully.")
        
        return user_profile
    except ResumeExtractionError as e:
        logger.error(f"Resume extraction error: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail=f"Failed to extract text from resume: {str(e)}"
        )
    except ProfileGenerationError as e:
        logger.error(f"Profile generation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to generate profile: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during profile building: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your profile."
        )
