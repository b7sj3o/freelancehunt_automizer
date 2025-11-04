"""Freelancehunt projects scraper implementation."""
from scraper.base import ProjectsScraperFactory
from schemas.project import MarketplaceEnum
from scraper.freelancehunt.selectors import ProjectsSelector, ProjectSelector
from core.config import settings
from core.browser import Browser
from core.loggers import freelancehunt_logger as logger


class FreelancehuntProjectsScraper(ProjectsScraperFactory):
    """Scraper for Freelancehunt projects."""
    
    def __init__(self, browser: Browser):
        super().__init__(browser)
        self.logger = logger
    
    @property
    def projects_selector_class(self):
        """Return the ProjectsSelector class for Freelancehunt."""
        return ProjectsSelector
    
    @property
    def project_selector_class(self):
        """Return the ProjectSelector class for Freelancehunt."""
        return ProjectSelector
    
    @property
    def marketplace_enum(self) -> MarketplaceEnum:
        """Return the MarketplaceEnum value for Freelancehunt."""
        return MarketplaceEnum.FREELANCEHUNT
    
    def get_projects_page_url(self, page: int) -> str:
        """Get URL for Freelancehunt projects listing page.
        
        Args:
            page: Page number
            
        Returns:
            URL string
        """
        return f"{settings.FREELANCEHUNT_PROJECTS_PAGE}&page={page}"
