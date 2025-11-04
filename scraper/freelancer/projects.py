"""Freelancer.com projects scraper implementation."""
from scraper.base import ProjectsScraperFactory
from schemas.project import MarketplaceEnum
from scraper.freelancer.selectors import ProjectsSelector, ProjectSelector
from core.config import settings
from core.browser import Browser
from core.loggers import freelancer_logger as logger


class FreelancerProjectsScraper(ProjectsScraperFactory):
    """Scraper for Freelancer.com projects."""
    
    def __init__(self, browser: Browser):
        super().__init__(browser)
        self.logger = logger
    
    @property
    def projects_selector_class(self):
        """Return the ProjectsSelector class for Freelancer."""
        return ProjectsSelector
    
    @property
    def project_selector_class(self):
        """Return the ProjectSelector class for Freelancer."""
        return ProjectSelector
    
    @property
    def marketplace_enum(self) -> MarketplaceEnum:
        """Return the MarketplaceEnum value for Freelancer."""
        return MarketplaceEnum.FREELANCER
    
    def get_projects_page_url(self, page: int) -> str:
        """Get URL for Freelancer projects listing page.
        
        Args:
            page: Page number
            
        Returns:
            URL string
        """
        return f"{settings.FREELANCER_PROJECTS_PAGE}&page={page}"
