import re

from selenium.webdriver.remote.webelement import WebElement

from ai.prompts import BASE_PROMPT
from ai.client import AI
from core.config import settings
from db.models import Project
from drivers.browser import Browser
from schemas.project import CreateProjectSchema, UpdateProjectSchema
from db.requests import create_projects, get_project, update_project
from utils.helpers import remove_markup
from core.loggers import projects_scraper_logger as logger
from scraper.freelancehunt import FreelancehuntProjectsScraper
from scraper.freelancer import FreelancerProjectsScraper

class ProjectsScraper:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.driver = browser.driver

        self.freelancehunt = FreelancehuntProjectsScraper(browser)
        self.freelancer = FreelancerProjectsScraper(browser)
    
        if not self.driver:
            raise ValueError("Driver is not initialized")