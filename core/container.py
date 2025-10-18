"""Dependency Injection Container."""
from db import Session
from db.repositories import ProjectRepository
from drivers.browser import Browser
from auth import Authenticator
from scraper.freelancehunt import FreelancehuntProjectsScraper
from scraper.freelancer import FreelancerProjectsScraper
from services import ProjectService


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
    def authenticator(self) -> Authenticator:
        """Get authenticator instance."""
        return Authenticator(self.browser)
    
    @property
    def project_repository(self) -> ProjectRepository:
        """Get project repository instance."""
        return ProjectRepository(self.db_session)
    
    @property
    def freelancehunt_scraper(self) -> FreelancehuntProjectsScraper:
        """Get Freelancehunt scraper instance."""
        return FreelancehuntProjectsScraper(self.browser)
    
    @property
    def freelancer_scraper(self) -> FreelancerProjectsScraper:
        """Get Freelancer scraper instance."""
        return FreelancerProjectsScraper(self.browser)
    
    @property
    def freelancehunt_project_service(self) -> ProjectService:
        """Get project service for Freelancehunt."""
        return ProjectService(
            repository=self.project_repository,
            scraper=self.freelancehunt_scraper
        )
    
    @property
    def freelancer_project_service(self) -> ProjectService:
        """Get project service for Freelancer."""
        return ProjectService(
            repository=self.project_repository,
            scraper=self.freelancer_scraper
        )
    
    def cleanup(self):
        """Cleanup resources."""
        if self._browser:
            self._browser.close_driver()
            self._browser = None
        if self._session:
            self._session.close()
            self._session = None

