"""Base repository interface."""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional


T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Base repository interface for all repositories."""
    
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self) -> list[T]:
        """Get all entities."""
        pass
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity."""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an existing entity."""
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        """Delete an entity by ID."""
        pass

