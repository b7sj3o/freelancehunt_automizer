"""Dependency Injection Container."""
from db import Base, Session, engine
from db.repositories import ProjectRepository
from schemas.project import MarketplaceEnum
from scraper import get_scraper
from scraper.base import ProjectsScraperFactory
from services import ProjectService
from core.browser import Browser
from core.loggers import db_logger as logger


class Container:
    """Dependency injection container for the application."""
    
    def __init__(self):
        self._browser = None
        self._session = None
    
    @property
    def browser(self) -> Browser:
        """Get browser instance (singleton)."""
        if self._browser is None:
            self._browser = Browser()
        return self._browser
    
    @property
    def db_session(self):
        """Get database session (new instance each time)."""
        return Session()
    
    @property
    def project_repository(self) -> ProjectRepository:
        """Get project repository instance."""
        return ProjectRepository(self.db_session)
 
 
    def start_db(self):
        """Start the database."""
        logger.info("Starting the database...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database was started.")


    def drop_db(self):
        """Drop the database."""
        logger.info("Dropping the database...")
        if input("Are you sure you want to drop the database? (y/N): ").lower() == "y":
            Base.metadata.drop_all(bind=engine)
            logger.info("Database was dropped.")
        else:
            logger.info("Database wasn't dropped.")
            exit(1)
    
    def cleanup(self):
        """Cleanup resources."""
        if self._browser:
            self._browser.close_driver()
            self._browser = None
        if self._session:
            self._session.close()
            self._session = None
        

