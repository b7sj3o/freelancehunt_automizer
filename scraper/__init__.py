from scraper.freelancehunt import FreelancehuntProjectsScraper
from scraper.freelancer import FreelancerProjectsScraper
from scraper.base import ProjectsScraperFactory
from schemas.project import MarketplaceEnum

SCRAPERS = {
    MarketplaceEnum.FREELANCEHUNT: FreelancehuntProjectsScraper,
    MarketplaceEnum.FREELANCER: FreelancerProjectsScraper,
}

def get_scraper(marketplace: MarketplaceEnum, browser) -> ProjectsScraperFactory:
    scraper_class = SCRAPERS.get(marketplace)
    if not scraper_class:
        raise ValueError(f"Unknown marketplace: {marketplace}")
    return scraper_class(browser)