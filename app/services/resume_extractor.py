from fastapi import UploadFile
import pdfplumber
import docx

async def extract_text_from_pdf(file: UploadFile) -> str:
    # Read into memmory
    contents = await file.read()
    
    # pdfplumber expects file like object, so use BytesIO
    import io
    with pdfplumber.open(io.BytesIO(contents), 'r') as pdf:
        # Join the pages' text
        return "\n".join([page.extract_text() or "" for page in pdf.pages])
        
async def extract_text_from_docx(file: UploadFile) -> str:
    # Read into memory
    contents = await file.read()
    
    # Docx expects file like object, so use BytesIO
    import io
    document = docx.Document(io.BytesIO(contents))
    # Join all paragraphs
    return "\n".join([paragraph.text for paragraph in document.paragraphs])

async def extract_resume_text(file: UploadFile) -> str:
    # Detect extension (robust to uppercase/lowercase)
    file_name = file.filename.lower()
    if file_name.endswith(".pdf"):
        return await extract_text_from_pdf(file)
    elif file_name.endswith(".docx"):
        return await extract_text_from_docx(file)
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are supported.")
    