import logging
from langchain.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.callbacks import AsyncCallbackHandler

from app.core import settings
from app.models.user_profile import UserProfile


logger = logging.getLogger(__name__)

class ProfileGenerationError(BaseException):
    pass

class ProfileCallbackHandler(AsyncCallbackHandler):
    async def on_llm_start(self, *args, **kwargs):
        logger.info("Starting LLM call....")
        
    async def on_llm_end(self, response, **kwargs):
        logger.info("LLM call completed successfully")
        
    async def on_llm_error(self, error, **kwargs):
        logger.error(f"LLM error: {str(error)}")
        raise ProfileGenerationError(f"LLM error: {str(error)}")

openai_ai_key = settings.OPENAI_API_KEY
if not openai_ai_key:
    logger.error("OPENAI_API_KEY value missing.")
    raise ValueError("OPENAI_API_KEY value missing. Check your environment variables.")

parser = PydanticOutputParser(pydantic_object=UserProfile)

PROMPT_TEXT = """
You are an expert resume parser with deep understanding of professional profiles.
Your job is to extract structured information from the provided resume text while handling various edge cases and ambiguities.

Input: Resume text in any structure, language or format
Ouput: Valid JSON object following the UserProfile schema

Processing Guidelines:

1. Name Extraction:
    - Look for the most prominent name at the top of the resume text
    - Handle various name formats (e.g., "John Doe", "Doe, John")
    - If ambiguous, use the most complete form
    - Validate name format (no special characters, proper capitalization)
    
2. Contact Information:
    - Email: Extract and validate format
    - Location: Standardize to City, Country format
    - Social Links: Validate URLs and categorize by platform
    - Handle multiple contact methods (priortize professional email)
    
3. Professional Information:
    - Headline: Extract current role or most recent position (max 100 chars)
    - Summary: Condense professional summary to key points (max 500 chars)
    - Skills: Categorize and assign proficiency levels (1-5)
    - Experience: Extract with dates, handling "present" and date ranges
    - Education: Extract with dates and degree information
    - Certification: Extract with name, authority and year
    - Languages: Categorize and assign proficiency levels ('Basic', 'Fluent', 'Native')
    
4. Project Information:
    - Extract project titles and descriptions
    - Identify technologies used in each project
    - Extract project dates (start and end)
    - Extract project URLs (if available)
    - Extract project role and responsibilities
    - Extract project highlights and achievements
    - Handle both personal and professional projects
    - Categorize projects by type (e.g., academic, professional, personal)
    
5. Error Handling:
    - Missing Dates: use null for unknown dates
    - Ambiguous Information: Use most likely interpretation
    - Inavlid URLs: Skip or mark as invalid
    - Unclear Skill Levels: Default to null
    - Unclear Experience: Default to null
    - Unclear Education: Default to null
    - Unclear Certifications: Default to null
    - Unclear Languages: Default to null
    - Unclear Projects: Default to null
    - Malformed Dates: Use null and log warning
    - Multiple Emails: Use most professional one
    - Conflicting Information: Use most recent/complete

6. Data Validation:
    - Ensure all dates are YYYY-MM-DD format
    - Validate all URLs are HTTP/HTTPS format
    - Verify email addresses are properly formatted
    - Check skill names are valid and proficiency levels are within range 1-5
    - Check experience names and company names are valid (no special characters)
    - Check education start date is not in the future
    - Check certification years are not in the future
    - Check language names are valid and proficiency levels are either "Basic", "Fluent" or "Native"
    - Validate headline length (max 100 chars)
    - Validate summary length (max 500 chars)
    - Validate company names (no special characters)
    - Validate institution names (no special characters)
    - Validate project titles and descriptions
    - Validate project technologies
    - Validate project URLs
    - Validate project dates
    
7. Output Formats:
    - Follow the UserProfile schema exactly
    - Include all required fields
    - Mark all optional fields as null if not found
    - Maintain proper JSON structure
    - Handle bullet points in descriptions
    - Handle formatting (bold, italic, etc)
    - Handle section headers
    - Handle abbreviations
    
8. Special Cases:
    - Handle multiple languages with proficiency levels
    - Process certifications with dates and authorities
    - Extract and validate social media profiles
    - Handle different date formats and ranges
    - Handle different resume formats (chronological, functional, hybrid)
    - Handle different date formats (MM/YYYY, Month YYYY, etc.)
    - Handle different skill categorization methods
    - Handle different education systems (e.g., GPA formats)
    - Handle different project formats and structures
    - Handle project dependencies and relationships
    
9. Data Quality:
    - Handle duplicate entries (remove duplicates)
    - Handle inconsistent information (use most recent)
    - Handle outdated information (mark as historical)
    - Handle incomplete information (use null for missing fields)
    - Handle project dependencies and relationships
    - Handle project technology stacks
    - Handle project achievements and metrics
    
Example Edge Cases:
1. "Present" dates: Convert to null for end_date
2. Date ranges: Extract start and end date separately
3. Multiple roles at same company: Create separate experience entries
4. Unclear skill levels: Set proficiency_level to null
5. Invalid URLs: Skip or mark as invalid
6. Malformed dates: Use null and log warning
7. Multiple emails: Use most professional one
8. Conflicting information: Use most recent/complete
9. Project dependencies: Handle related projects
10. Project technologies: Handle technology stacks
11. Project metrics: Handle numerical achievements
12. Project roles: Handle multiple roles in same project

Example Output:
{
    "full_name": "John Doe",
    "email": "john.doe@example.com",
    "headline": "Senior Software Engineer",
    "summary": "Experienced software engineer with expertise in...",
    "location": "New York, USA",
    "skills": [
        {"name": "Python", "proficiency_level": 5, "verified": true},
        {"name": "JavaScript", "proficiency_level": 4}
    ],
    "experience": [
        {
            "name": "Senior Developer",
            "company": "Tech Corp",
            "start_date": "2020-01-01",
            "end_date": null,
            "description": "Led development of..."
        }
    ],
    "projects": [
        {
            "title": "E-commerce Platform",
            "description": "Built a scalable e-commerce platform",
            "technologies": ["Python", "Django", "React"],
            "start_date": "2021-01-01",
            "end_date": "2021-06-30",
            "url": "https://github.com/johndoe/ecommerce",
            "role": "Lead Developer",
            "highlights": [
                "Implemented real-time inventory management",
                "Reduced checkout time by 50%"
            ]
        }
    ]
}

Resume Text:
{resume_text}

Extract and output JSON for this schema:
{format_instructions}
"""

prompt = PromptTemplate.from_template(PROMPT_TEXT)

llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.0,
    api_key=openai_ai_key,
    max_tokens=2000,
    callbacks={ProfileCallbackHandler()}
)

async def generate_profile_llm(resume_text: str) -> UserProfile:
    format_instructions = parser.get_format_instructions()
    chain = prompt | llm | parser

    try:
        logger.info("Starting profile generation...")
        result = await chain.invoke({
            "resume_text": resume_text,
            "format_instructions": format_instructions
        })
        logger.info("Profile generated successfully.")
        return result
    except OutputParserException as e:
        logger.error(f"Output parsing error: {str(e)}")
        raise ProfileGenerationError(f"Failed to parse LLM output: {str(e)}")
    except Exception as e:
        logger.error(f"Profile generation error: {str(e)}")
        raise ProfileGenerationError(f"Failed to generate profile: {str(e)}")