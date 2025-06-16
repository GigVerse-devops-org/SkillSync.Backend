from typing import Optional
from uuid import UUID
import logging
from app.domain.company.models import Company
from app.infrastructure.supabase_client import SupabaseClient
from app.repositories.base import BaseRepository
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

class CompanyRepository(BaseRepository[Company]):
    def __init__(self):
        self.client = SupabaseClient.get_instance()
        self.table = "companies"
        
    async def create(self, company: Company) -> Company:
        try:
            data = company.model_dump()
            result = self.client.table(self.table).insert(data).execute()
            return Company(**result.data[0])
        except Exception as e:
            logger.error(f"Failed to create company: {str(e)}")
            raise AppException("Failed to create company in DB.")
    
    async def get_by_name(self, company_name: str) -> Optional[Company]:
        try:
            result = self.client.table(self.table).select('*').eq('company_name', company_name).execute()
            return Company(**result.data[0]) if result.data else None
        except Exception as e:
            logger.error(f"Failed to get company by name: {str(e)}")
            raise AppException("Failed to get company by name.")
    
    async def get_by_id(self, company_id: UUID) -> Optional[Company]:
        try:
            result = self.client.table(self.table).select('*').eq('id', str(company_id)).execute()
            return Company(**result.data[0]) if result.data else None
        except Exception as e:
            logger.error(f"Failed to get company by id: {str(e)}")
            raise AppException("Failed to get company by id.")