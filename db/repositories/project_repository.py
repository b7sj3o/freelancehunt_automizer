"""Project repository implementation."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db.models import Project
from db.repositories.base import BaseRepository
from schemas.project import CreateProjectSchema, UpdateProjectSchema
from core.exceptions import ProjectNotFoundError, DuplicateProjectError, DatabaseError
from core.loggers import db_logger as logger


class ProjectRepository(BaseRepository[Project]):
    """Repository for Project entity."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, id: int) -> Optional[Project]:
        """Get project by ID."""
        try:
            return self.session.get(Project, id)
        except Exception as e:
            logger.error(f"Failed to get project by id {id}: {e}")
            raise DatabaseError(f"Failed to get project: {e}") from e
    
    def get_by_link(self, link: str) -> Optional[Project]:
        """Get project by link."""
        try:
            return self.session.scalars(
                select(Project).where(Project.link == link)
            ).first()
        except Exception as e:
            logger.error(f"Failed to get project by link {link}: {e}")
            raise DatabaseError(f"Failed to get project: {e}") from e
    
    def get_all(self) -> list[Project]:
        """Get all projects."""
        try:
            return list(self.session.scalars(select(Project)).all())
        except Exception as e:
            logger.error(f"Failed to get all projects: {e}")
            raise DatabaseError(f"Failed to get projects: {e}") from e
    
    def get_active_projects(self) -> list[Project]:
        """Get projects that don't have bids placed and are not skipped."""
        try:
            return list(self.session.scalars(
                select(Project)
                .where(Project.is_bid_placed.is_(False))
                .where(Project.is_bid_skipped.is_(False))
            ).all())
        except Exception as e:
            logger.error(f"Failed to get active projects: {e}")
            raise DatabaseError(f"Failed to get active projects: {e}") from e
    
    def create(self, project_data: CreateProjectSchema) -> Project:
        """Create a new project."""
        try:
            # Check if project with this link already exists
            existing = self.get_by_link(project_data.link)
            if existing:
                raise DuplicateProjectError(f"Project with link {project_data.link} already exists")
            
            project = Project(**project_data.model_dump())
            self.session.add(project)
            self.session.commit()
            self.session.refresh(project)
            
            logger.info(f"Created project: {project.title} (ID: {project.id})")
            return project
            
        except DuplicateProjectError:
            raise
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Integrity error creating project: {e}")
            raise DuplicateProjectError(f"Project already exists: {e}") from e
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to create project: {e}")
            raise DatabaseError(f"Failed to create project: {e}") from e
    
    def create_many(self, projects_data: list[CreateProjectSchema]) -> list[Project]:
        """Create multiple projects at once."""
        created_projects = []
        
        for project_data in projects_data:
            try:
                # Check if already exists
                if self.get_by_link(project_data.link):
                    logger.debug(f"Project with link {project_data.link} already exists, skipping")
                    continue
                
                project = Project(**project_data.model_dump())
                self.session.add(project)
                created_projects.append(project)
                
            except Exception as e:
                logger.warning(f"Failed to prepare project {project_data.title}: {e}")
                continue
        
        try:
            self.session.commit()
            
            # Refresh all created projects
            for project in created_projects:
                self.session.refresh(project)
            
            logger.info(f"Created {len(created_projects)} projects")
            return created_projects
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to create projects batch: {e}")
            raise DatabaseError(f"Failed to create projects: {e}") from e
    
    def update(self, project_id: int, update_data: UpdateProjectSchema) -> Project:
        """Update project."""
        try:
            project = self.get_by_id(project_id)
            if not project:
                raise ProjectNotFoundError(f"Project with id {project_id} not found")
            
            # Update only provided fields
            data_dict = update_data.model_dump(exclude_none=True, exclude_unset=True)
            for key, value in data_dict.items():
                setattr(project, key, value)
            
            self.session.commit()
            self.session.refresh(project)
            
            logger.info(f"Updated project: {project.title} (ID: {project.id}), data: {data_dict}")
            return project
            
        except ProjectNotFoundError:
            raise
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to update project {project_id}: {e}")
            raise DatabaseError(f"Failed to update project: {e}") from e
    
    def delete(self, id: int) -> bool:
        """Delete project by ID."""
        try:
            project = self.get_by_id(id)
            if not project:
                raise ProjectNotFoundError(f"Project with id {id} not found")
            
            self.session.delete(project)
            self.session.commit()
            
            logger.info(f"Deleted project: {project.title} (ID: {id})")
            return True
            
        except ProjectNotFoundError:
            raise
        except Exception as e:
            self.session.rollback()
            logger.error(f"Failed to delete project {id}: {e}")
            raise DatabaseError(f"Failed to delete project: {e}") from e
    
    def exists_by_link(self, link: str) -> bool:
        """Check if project with given link exists."""
        return self.get_by_link(link) is not None

