"""Base scraper interfaces."""
from abc import ABC, abstractmethod
from typing import Optional

from db.models import Project
from schemas.project import CreateProjectSchema


class BaseProjectScraper(ABC):
    """Base interface for project scrapers."""
    
    @abstractmethod
    def scrape_projects_list(self, page: int = 1) -> list[CreateProjectSchema]:
        """Scrape projects from a listing page.
        
        Args:
            page: Page number to scrape
            
        Returns:
            List of project schemas (not saved to DB yet)
        """
        pass
    
    @abstractmethod
    def scrape_project_details(self, project: Project) -> dict:
        """Scrape detailed information from project page.
        
        Args:
            project: Project model from database
            
        Returns:
            Dictionary with project details including description
        """
        pass
    
    @abstractmethod
    def submit_bid(self, project: Project, message: str) -> bool:
        """Submit a bid on a project.
        
        Args:
            project: Project to bid on
            message: Bid message to submit
            
        Returns:
            True if bid was successfully submitted
        """
        pass
    
    @abstractmethod
    def check_bid_status(self, project: Project) -> dict:
        """Check current bid status on project page.
        
        Args:
            project: Project to check
            
        Returns:
            Dictionary with bid status info (e.g., already_bid, no_more_bids, etc.)
        """
        pass
