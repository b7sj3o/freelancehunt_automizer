"""Project service for business logic."""

from ai.client import AI
from ai.prompts import BASE_PROMPT
from db.models import Project
from db.repositories.project_repository import ProjectRepository
from scraper.base import ProjectsScraperFactory
from schemas.project import UpdateProjectSchema
from core.loggers import db_logger as logger
from core.exceptions import (
    AIResponseError,
    BidAlreadyPlacedError,
    NoMoreBidsError,
    TooManyBidsError,
    BidSubmissionError,
    ScrapingError
)


class ProjectService:
    """Service for managing projects and bidding logic."""
    
    def __init__(
        self, 
        repository: ProjectRepository,
        scraper: ProjectsScraperFactory,
    ):
        self.repository = repository
        self.scraper = scraper
        
    
    def scrape_and_save_projects(self, page: int) -> int:
        """Scrape projects from a page and save to database.
        
        Args:
            page: Page number to scrape
            
        Returns:
            Number of new projects saved
        """
        try:
            # Scrape projects (scraper doesn't touch DB)
            projects_data = self.scraper.scrape_projects_list(page)
            logger.info(f"Scraped {len(projects_data)} projects from page {page}")
            
            # Filter out existing projects
            new_projects = []
            for project_data in projects_data:
                if not self.repository.exists_by_link(project_data.link):
                    new_projects.append(project_data)
            
            logger.info(f"Found {len(new_projects)} new projects (filtered {len(projects_data) - len(new_projects)} duplicates)")
            
            # Save to database
            if new_projects:
                saved = self.repository.create_many(new_projects)
                logger.info(f"Saved {len(saved)} new projects to database")
                return len(saved)
            
            return 0
            
        except ScrapingError as e:
            logger.error(f"Scraping error on page {page}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error scraping page {page}: {e}", exc_info=True)
            raise
    
    def get_active_projects(self) -> list[Project]:
        """Get all active projects (no bid placed, not skipped)."""
        return self.repository.get_active_projects()
    
    def process_project(self, project: Project) -> bool:
        """Process a project - check status, get AI response, place bid if needed.
        
        Args:
            project: Project to process
            
        Returns:
            True if bid was placed, False otherwise
        """
        logger.info(f"Processing project: {project.title} ({project.link})")
        
        try:
            # Check bid status first
            status = self.scraper.check_bid_status(project)
            
            # Handle different statuses
            if status["already_bid"]:
                logger.info(f"Bid already placed on {project.title}, marking in DB")
                self.repository.update(project.id, UpdateProjectSchema(is_bid_placed=True))
                return True
            
            if status["no_more_bids"]:
                logger.info(f"No more bids allowed on {project.title}, skipping")
                self.repository.update(project.id, UpdateProjectSchema(is_bid_skipped=True))
                return False
            
            if status["too_many_bids"]:
                logger.warning(f"Too many bids on {project.title}, skipping")
                self.repository.update(project.id, UpdateProjectSchema(is_bid_skipped=True))
                return False
            
            # If we can bid, get project details and AI response
            if status["can_bid"]:
                return self._process_bidding(project)
            
            return False
            
        except (BidAlreadyPlacedError, NoMoreBidsError, TooManyBidsError) as e:
            logger.info(f"Cannot bid on {project.title}: {e}")
            self.repository.update(project.id, UpdateProjectSchema(is_bid_skipped=True))
            return False
            
        except Exception as e:
            logger.error(f"Error processing project {project.title}: {e}", exc_info=True)
            # Mark as skipped on any error to avoid reprocessing
            self.repository.update(project.id, UpdateProjectSchema(is_bid_skipped=True))
            return False
    
    def _process_bidding(self, project: Project) -> bool:
        """Process bidding logic with AI.
        
        Args:
            project: Project to bid on
            
        Returns:
            True if bid was placed
        """
        try:
            # Get project details
            details = self.scraper.scrape_project_details(project)
            description = details.get("description", "")
            
            if not description:
                logger.warning(f"No description found for {project.title}, skipping")
                self.repository.update(project.id, UpdateProjectSchema(is_bid_skipped=True))
                return False
            
            # Get AI response
            logger.info(f"Getting AI response for {project.title}")
            prompt = BASE_PROMPT.format(project_description=description)
            message = AI.prompt_to_ai(prompt)
            
            if not message:
                logger.error(f"AI returned empty response for {project.title}")
                # Don't mark as skipped - retry later
                return False
            
            logger.info(f"AI response for {project.title}: {message[:100]}...")
            
            # Check if AI decided to skip
            if message.lower() == "false":
                logger.info(f"AI decided to skip {project.title}")
                self.repository.update(project.id, UpdateProjectSchema(is_bid_skipped=True))
                return False
            
            # Submit bid
            logger.info(f"Submitting bid on {project.title}")
            success = self.scraper.submit_bid(project, message)
            
            if success:
                logger.info(f"Successfully placed bid on {project.title}")
                self.repository.update(
                    project.id, 
                    UpdateProjectSchema(bid_message=message, is_bid_placed=True)
                )
                return True
            else:
                logger.warning(f"Failed to place bid on {project.title}")
                return False
            
        except BidSubmissionError as e:
            logger.error(f"Bid submission failed for {project.title}: {e}")
            # Don't skip - might be temporary error
            return False
            
        except AIResponseError as e:
            logger.error(f"AI error for {project.title}: {e}")
            return False
            
        except Exception as e:
            logger.error(f"Unexpected error in bidding process for {project.title}: {e}", exc_info=True)
            # Mark as skipped to avoid infinite retries
            self.repository.update(project.id, UpdateProjectSchema(is_bid_skipped=True))
            return False

