from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class Company(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    company_name: str
    registration_number: Optional[str] = None
    country: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)