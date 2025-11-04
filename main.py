"""Main application entry point."""
import logging

from auth import get_authenticator
from core.container import Container
from core.loggers import freelancehunt_logger, freelancer_logger
from core.exceptions import AuthenticationError, ScrapingError, DatabaseError
from schemas.project import MarketplaceEnum
from services import ProjectService
from scraper import get_scraper


class Application:
    def __init__(self, container: Container):
        self.container = container
        self.container.start_db()
    
    def get_pages_range(self, tries: int = 5) -> tuple[int, int]:
        """Get pages range from user input.
        
        Args:
            tries: Number of tries for input validation
            
        Returns:
            Tuple of (start_page, end_page)
            
        Raises:
            ValueError: If all tries were exceeded
        """
        if tries == 0:
            raise ValueError("All tries were exceeded")
        
        pages = input("Enter amount of pages you want to parse (to) or (from,to): ").strip()
        
        # Single number means from 1 to that number
        if pages.isdigit():
            return (1, int(pages) + 1)
        
        # Range format: "from,to"
        try:
            parts = pages.split(",")
            if len(parts) != 2:
                print("Invalid format. Use: '5' or '1,5'")
                return self.get_pages_range(tries - 1)
            
            n_from, n_to = map(str.strip, parts)
            
            if not n_from.isdigit() or not n_to.isdigit():
                print("Both values must be numbers")
                return self.get_pages_range(tries - 1)
            
            start, end = int(n_from), int(n_to)
            
            if start < 1 or end < start:
                print("Invalid range. Start must be >= 1 and end >= start")
                return self.get_pages_range(tries - 1)
            
            return (start, end + 1)
            
        except Exception as e:
            print(f"Error parsing input: {e}")
            return self.get_pages_range(tries - 1)
    
    def scrape_and_process_projects(
        self, 
        service: ProjectService,
        logger: logging.Logger,
        marketplace: MarketplaceEnum
    ) -> None:
        """Scrape projects and process them with bids.
        
        Args:
            service: ProjectService instance
            logger: Logger for this marketplace
            marketplace: MarketplaceEnum
        """
        logger.info(f"Starting {marketplace.value} automation")
        
        try:
            # Scrape projects from multiple pages
            start_page, end_page = self.get_pages_range()
            total_scraped = 0
            
            for page in range(start_page, end_page):
                try:
                    count = service.scrape_and_save_projects(page)
                    total_scraped += count
                    logger.info(f"Page {page}: scraped {count} new projects")
                except ScrapingError as e:
                    logger.error(f"Failed to scrape page {page}: {e}")
                    continue
            
            logger.info(f"Total new projects scraped: {total_scraped}")
            
            # Get active projects and process them
            projects = service.get_active_projects()
            logger.info(f"Found {len(projects)} active projects to process")
            
            projects_bid_placed = 0
            projects_skipped = 0
            
            for project in projects:
                try:
                    is_bid_placed = service.process_project(project)
                    
                    if is_bid_placed:
                        logger.info(f"✓ Bid placed: {project.title}")
                        projects_bid_placed += 1
                    else:
                        logger.info(f"⊗ Bid skipped: {project.title}")
                        projects_skipped += 1
                        
                except DatabaseError as e:
                    logger.error(f"Database error for {project.title}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error for {project.title}: {e}", exc_info=True)
                    continue
            
            # Summary
            logger.info("=" * 50)
            logger.info(f"{marketplace.value} Summary:")
            logger.info(f"  New projects scraped: {total_scraped}")
            logger.info(f"  Bids placed: {projects_bid_placed}")
            logger.info(f"  Projects skipped: {projects_skipped}")
            logger.info("=" * 50)
            
        except Exception as e:
            logger.error(f"Critical error in {marketplace.value} automation: {e}", exc_info=True)
            raise
    
    def run(self, marketplace: MarketplaceEnum, logger: logging.Logger) -> None:
        """Run full automation for all marketplaces."""
        try:
            # Authenticate
            authenticator = get_authenticator(marketplace, self.container.browser)
            authenticator.login()
            
            # Process projects
            scraper = get_scraper(marketplace, self.container.browser)
            service = ProjectService(
                repository=self.container.project_repository,
                scraper=scraper
            )
            self.scrape_and_process_projects(
                service=service,
                logger=logger,
                marketplace=marketplace
            )
        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            raise
        except Exception as e:
            logger.error(f"{marketplace.value} automation failed: {e}", exc_info=True)
            raise


def main():
    """Application entry point."""
    container = Container()
    app = Application(container)
    
    try:
        app.run(MarketplaceEnum.FREELANCEHUNT, freelancehunt_logger)
        #  app.run(MarketplaceEnum.FREELANCER, freelancer_logger) # ! TODO Потрібно реалізувати селектори 
    except KeyboardInterrupt:
        print("\n\nAutomation interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        raise
    finally:
        container.cleanup()


if __name__ == "__main__":
    main()
    