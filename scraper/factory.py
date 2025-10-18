from drivers.browser import Browser
from scraper.base import BaseProjectScraper
from scraper.freelancehunt import FreelancehuntProjectsScraper
from scraper.freelancer import FreelancerProjectsScraper

SCRAPERS = {
    "freelancehunt": FreelancehuntProjectsScraper,
    "freelancer": FreelancerProjectsScraper,
}

def get_scraper(service_name: str, browser: Browser) -> BaseProjectScraper:
    scraper_class = SCRAPERS.get(service_name.lower())
    if not scraper_class:
        raise ValueError(f"Unknown service: {service_name}")
    return scraper_class(browser)
