"""Base scraper interfaces."""
from abc import ABC, abstractmethod
from typing import Optional
import re

from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

from db.models import Project
from schemas.project import CreateProjectSchema, MarketplaceEnum
from utils.helpers import remove_markup
from core.config import settings
from core.browser import Browser
from core.exceptions import (
    ElementNotFoundError, 
    ParsingError, 
    PageLoadError,
    BidSubmissionError
)


class ProjectsScraperFactory(ABC):
    """Base class for project scrapers with common implementation."""
    
    def __init__(self, browser: Browser):
        """Initialize scraper with browser instance.
        
        Args:
            browser: Browser instance with initialized driver
        """
        self.browser = browser
        self.driver = browser.driver
        
        if not self.driver:
            raise ValueError("Driver is not initialized")
    
    @property
    @abstractmethod
    def projects_selector_class(self):
        """Return the ProjectsSelector class for this marketplace."""
        pass
    
    @property
    @abstractmethod
    def project_selector_class(self):
        """Return the ProjectSelector class for this marketplace."""
        pass
    
    @property
    @abstractmethod
    def marketplace_enum(self) -> MarketplaceEnum:
        """Return the MarketplaceEnum value for this marketplace."""
        pass
    
    @abstractmethod
    def get_projects_page_url(self, page: int) -> str:
        """Get URL for projects listing page.
        
        Args:
            page: Page number
            
        Returns:
            URL string
        """
        pass
    
    def _extract_price(self, row: WebElement) -> tuple[int, str]:
        """Extract price and currency from project row.
        
        Args:
            row: WebElement containing project row
            
        Returns:
            Tuple of (price, currency)
        """
        try:
            ProjectsSelector = self.projects_selector_class
            price_text = row.find_element(*ProjectsSelector.PRICE).get_attribute("innerHTML").strip()
            *prices, currency = price_text.split()
            price = "".join(prices)
            return int(price), currency
        except Exception as e:
            # Use logger from child class if available
            logger = getattr(self, 'logger', None)
            if logger:
                logger.warning("Failed to extract price, using default")
            return settings.DEFAULT_PRICE_UAH, "UAH"
    
    def scrape_projects_list(self, page: int = 1) -> list[CreateProjectSchema]:
        """Scrape projects from listing page.
        
        Args:
            page: Page number to scrape
            
        Returns:
            List of CreateProjectSchema (not saved to DB)
        """
        ProjectsSelector = self.projects_selector_class
        logger = getattr(self, 'logger', None)
        
        try:
            url = self.get_projects_page_url(page)
            if logger:
                logger.info(f"Scraping projects from page {page}: {url}")
            self.driver.get(url)
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to load page {page}: {e}")
            raise PageLoadError(f"Failed to load projects page: {e}") from e
        
        projects = []
        
        try:
            rows = self.driver.find_elements(*ProjectsSelector.ALL_PROJECTS)
            if logger:
                logger.info(f"Found {len(rows)} project rows on page {page}")
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to find project rows: {e}")
            raise ElementNotFoundError("Failed to find project rows") from e
        
        for row in rows:
            try:
                title_el = row.find_element(*ProjectsSelector.TITLE)
                title = title_el.text.strip()
                link = title_el.get_attribute("href")
                
                if not title or not link:
                    if logger:
                        logger.warning("Empty title or link, skipping")
                    continue
                
                price, currency = self._extract_price(row)
                
                projects.append(CreateProjectSchema(
                    title=title,
                    link=link,
                    price=price,
                    currency=currency,
                    marketplace=self.marketplace_enum
                ))
                
            except NoSuchElementException as e:
                if logger:
                    logger.warning(f"Failed to parse project row: {e}")
                continue
            except Exception as e:
                if logger:
                    logger.error(f"Unexpected error parsing project: {e}", exc_info=True)
                continue
        
        if logger:
            logger.info(f"Successfully scraped {len(projects)} projects from page {page}")
        return projects
    
    def scrape_project_details(self, project: Project) -> dict:
        """Scrape detailed information from project page.
        
        Args:
            project: Project model
            
        Returns:
            Dictionary with project details
        """
        ProjectSelector = self.project_selector_class
        logger = getattr(self, 'logger', None)
        
        try:
            if logger:
                logger.info(f"Opening project page: {project.link}")
            self.driver.get(project.link)
            
        except Exception as e:
            if logger:
                logger.error(f"Failed to load project page {project.link}: {e}")
            raise PageLoadError(f"Failed to load project page: {e}") from e
        
        try:
            description_el = self.driver.find_element(*ProjectSelector.DESCRIPTION)
            description_html = description_el.get_attribute("innerHTML")
            description = remove_markup(description_html)
            
            return {
                "description": description,
                "link": project.link,
                "title": project.title
            }
            
        except NoSuchElementException as e:
            if logger:
                logger.error(f"Failed to find description element: {e}")
            raise ElementNotFoundError("Project description not found") from e
        except Exception as e:
            if logger:
                logger.error(f"Failed to scrape project details: {e}")
            raise ParsingError(f"Failed to parse project details: {e}") from e
    
    def check_bid_status(self, project: Project) -> dict:
        """Check bid status on project page.
        
        Returns:
            Dictionary with status info:
            {
                "already_bid": bool,
                "no_more_bids": bool,
                "too_many_bids": bool,
                "can_bid": bool
            }
        """
        ProjectSelector = self.project_selector_class
        logger = getattr(self, 'logger', None)
        
        try:
            self.driver.get(project.link)
        except Exception as e:
            if logger:
                logger.error(f"Failed to load project page: {e}")
            raise PageLoadError(f"Failed to load project page: {e}") from e
        
        status = {
            "already_bid": False,
            "no_more_bids": False,
            "too_many_bids": False,
            "can_bid": True
        }
        
        # Check for "Already bid"
        try:
            self.driver.find_element(*ProjectSelector.ALREADY_BID)
            status["already_bid"] = True
            status["can_bid"] = False
            if logger:
                logger.info(f"Bid already placed on {project.link}")
        except NoSuchElementException:
            pass
        
        # Check for "No more bids"
        try:
            self.driver.find_element(*ProjectSelector.NO_MORE_BIDS)
            status["no_more_bids"] = True
            status["can_bid"] = False
            if logger:
                logger.info(f"No more bids allowed on {project.link}")
        except NoSuchElementException:
            pass
        
        # Check for "Too many bids"
        try:
            self.driver.find_element(*ProjectSelector.TOO_MANY_BIDS)
            status["too_many_bids"] = True
            status["can_bid"] = False
            if logger:
                logger.warning(f"Too many bids on {project.link}")
        except NoSuchElementException:
            pass
        
        return status
    
    def submit_bid(self, project: Project, message: str) -> bool:
        """Submit a bid on the project.
        
        Args:
            project: Project to bid on
            message: Bid message
            
        Returns:
            True if bid was successfully submitted
            
        Raises:
            BidSubmissionError: If bid submission fails
        """
        ProjectSelector = self.project_selector_class
        logger = getattr(self, 'logger', None)
        
        try:
            # Ensure we're on the project page
            if self.driver.current_url != project.link:
                self.driver.get(project.link)
            
            # Click "Place bid" button
            try:
                place_bid_button = self.driver.find_element(*ProjectSelector.PLACE_BID_BUTTON)
                place_bid_button.click()
                if logger:
                    logger.info("Clicked 'Place bid' button")
            except NoSuchElementException as e:
                if logger:
                    logger.error("Place bid button not found")
                raise ElementNotFoundError("Place bid button not found") from e
            
            # Fill message
            try:
                message_input = self.driver.find_element(*ProjectSelector.MESSAGE_INPUT)
                message_input.clear()
                message_input.send_keys(message)
                if logger:
                    logger.info("Filled bid message")
            except NoSuchElementException as e:
                if logger:
                    logger.error("Message input not found")
                raise ElementNotFoundError("Message input not found") from e
            
            # Fill days
            try:
                days_input = self.driver.find_element(*ProjectSelector.DAYS_INPUT)
                days_input.clear()
                days_input.send_keys(str(settings.DEFAULT_DAYS))
                if logger:
                    logger.info(f"Filled days: {settings.DEFAULT_DAYS}")
            except NoSuchElementException as e:
                if logger:
                    logger.error("Days input not found")
                raise ElementNotFoundError("Days input not found") from e
            
            # Fill price
            try:
                price_input = self.driver.find_element(*ProjectSelector.PRICE_INPUT)
                price_input.clear()
                price_input.send_keys(str(project.price))
                if logger:
                    logger.info(f"Filled price: {project.price}")
            except NoSuchElementException as e:
                if logger:
                    logger.error("Price input not found")
                raise ElementNotFoundError("Price input not found") from e
            
            # Submit bid
            try:
                submit_button = self.driver.find_element(*ProjectSelector.SUBMIT_BID_BUTTON)
                submit_button.click()
                if logger:
                    logger.info("Clicked 'Submit bid' button")
            except NoSuchElementException as e:
                if logger:
                    logger.error("Submit button not found")
                raise ElementNotFoundError("Submit button not found") from e
            
            # Check for errors
            try:
                self.driver.find_element(*ProjectSelector.ERROR_ALERT)
                error_texts = self.driver.find_elements(*ProjectSelector.ERROR_TEXT)
                error_text = "\n".join([text.text for text in error_texts])
                if logger:
                    logger.error(f"Bid submission error: {error_text}")
                raise BidSubmissionError(f"Bid submission failed: {error_text}")
            except NoSuchElementException:
                # No error alert - bid was successful
                if logger:
                    logger.info(f"Bid successfully submitted on {project.link}")
                return True
            
        except (ElementNotFoundError, BidSubmissionError):
            raise
        except Exception as e:
            if logger:
                logger.error(f"Unexpected error submitting bid: {e}", exc_info=True)
            raise BidSubmissionError(f"Failed to submit bid: {e}") from e

