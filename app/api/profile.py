import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.models.user_profile import UserProfile
from app.services.file_validation import validate_file, validate_file_content, FileValidationError
from app.services.profile_generator import ProfileGenerationError, generate_profile_llm
from app.services.resume_extractor import ResumeExtractionError, extract_resume_text

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/profile/build", response_model=UserProfile)
async def build_profile(
    file: UploadFile = File(None),
    profile_text: str = Form(None)
):
    logger.info("API request: '/profile/build' received.")

    if not file and not profile_text:
        logger.error("Must provide either a resume file or profile text")
        raise HTTPException(
            status_code=400, 
            detail="Must provide either a resume file or profile text."
        )

    try:
        validate_file(file)
        if file:
            logger.info(f"Processing uploaded file: {file.filename}")
            
            contents = await file.read()
            extension = file.filename[file.filename.rfind('.'):].lower()
            
            validate_file_content(contents, extension)
            
            logger.info("Extracting text from file...")
            resume_text = extract_resume_text(contents, extension)
            logger.info("Text extraction successfull.")
        else:
            resume_text = profile_text

        logger.info("Generating profile from text...")
        user_profile = await generate_profile_llm(resume_text)
        logger.info("Profile generated successfully.")
        return user_profile

    except FileValidationError as e:
        logger.error(f"File validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ResumeExtractionError as e:
        logger.error(f"Resume extraction error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to extract text from resume: {str(e)}")
    except ProfileGenerationError as e:
        logger.error(f"Profile generation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to generate profile: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during profile building: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your profile."
        )
