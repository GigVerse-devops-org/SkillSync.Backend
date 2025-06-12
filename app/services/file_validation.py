import logging
import os
import re
from typing import Optional
from fastapi import UploadFile
from app.core import settings

logger = logging.getLogger(__name__)

class FileValidationError(Exception):
    """Custom exception for file and content validation errors."""
    pass

def validate_file(file: Optional[UploadFile] = None) -> None:
    if not file:
        return
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in settings.ALLOWED_FILE_EXTENSIONS:
        logger.error(f"Unsupported file type: {extension}")
        raise FileValidationError(
            f"Unsupported file type. Allowed file types: {', '.join(settings.ALLOWED_FILE_EXTENSIONS)}"
        )
        
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        logger.error(f"Unsupported content type: {file.content_type}")
        raise FileValidationError(
            f"Unsupported content type. Allowed content types: {', '.join(settings.ALLOWED_MIME_TYPES)}"
        )
        
    file_size_mb: float = file.size / (1024 * 1024)
    if file_size_mb > settings.ALLOWED_FILE_SIZE_MB:
        logger.error(f"File size too large: {file_size_mb}MB.")
        raise FileValidationError(
            f"File size too large. Allowed file size: {settings.ALLOWED_FILE_SIZE_MB}MB"
        )

def validate_file_content(file_contents: bytes, file_extension: str) -> None:
    if not file_contents:
        raise FileValidationError("File is empty")
    
    if len(file_contents) < 100:
        raise FileValidationError("File is too small (less than 100 bytes)")
    
    if len(file_contents) > 10 * 1024 * 1024:
        raise FileValidationError("File is too large (more than 10MB)")
    
    if file_extension in [".docx", ".txt"]:
        if b'\x00' in file_contents:
            raise FileValidationError("File appears to be binary/executable instead of text")
        
    image_signatures = [
        b'\xFF\xD8\xFF',  # JPEG
        b'\x89PNG\r\n\x1a\n',  # PNG
        b'GIF87a',  # GIF
        b'GIF89a',  # GIF
        b'BM',  # BMP
    ]
    if any(file_contents.startswith(sig) for sig in image_signatures):
        raise FileValidationError("File appears to be an image instead of text")
    
    if file_extension == '.pdf':
        if not file_contents.startswith(b'%PDF-'):
            raise FileValidationError("Invalid PDF file format")
        if b'%%EOF' not in file_contents:
            raise FileValidationError("PDF file appears to be incomplete or corrupted")
        
    try:
        text = file_contents.decode('utf-8', errors='ignore')
        
        clean_text = re.sub(r'[\s\x00-\x1f\x7f-\xff]', '', text)
        if len(clean_text) < 50:
            raise FileValidationError("File contains insufficient text content")
        
        resume_keywords = [
            'experience', 'education', 'skills', 'work', 'job',
            'university', 'college', 'degree', 'certification'
        ]
        text_lower = text.lower()
        if not any(keyword in text_lower for keyword in resume_keywords):
            raise FileValidationError("File content doesn't appear to be a resume")
    except UnicodeDecodeError:
        raise FileValidationError("File contains invalid text encoding")