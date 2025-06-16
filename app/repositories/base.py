from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    """Base repository interface for common operations."""
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create an entity in the database."""
        pass
    
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Retrieve an entity by its ID."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """Retrieve all entities"""
        pass
    
    @abstractmethod
    async def update(self, id: UUID, entity: T) -> Optional[T]:
        """Update an existing entity"""
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete an existing entity by ID"""
        pass
        
    
"""
1. BaseRepository Class:
    . An abstract base class using Python's ABC (Abstract Base Class)
    . Generic type T to work with any entity type
    . Defines common CRUD operations that all repositories must implement

2. TypeVar: 
    . It allows functions, classes, and other structures to operate with multiple types while maintaining type safety.
    . TypeVar acts as a placeholder for a type that is determined at the time of function call or class instantiation.
    
3. Core Methods:
    . create: Create new entities
    . get_by_id: Retrieve by UUID
    . get_all: List all entities
    . update: Modify existing entities
    . delete: Remove entities
"""