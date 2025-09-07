import re

from selenium.webdriver.remote.webelement import WebElement

from ai.prompts import BASE_PROMPT
from ai.client import AI
from core.config import settings
from db.models import Project
from drivers.browser import Browser
from schemas.project import CreateProjectSchema, UpdateProjectSchema
from db.requests import create_projects, get_project, update_project
from scraper.selectors import ProjectsSelector, ProjectSelector
from utils.helpers import remove_markup
from core.logger_config import setup_logger

logger = setup_logger(name="projects_scraper", log_file="projects_scraper.log")

class ProjectsScraper:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.driver = browser.driver

        if not self.driver:
            raise ValueError("Driver is not initialized")


    def extract_bids(self, row: WebElement) -> int:
        try:
            bids_text = row.find_element(*ProjectsSelector.BIDS).text
        except:
            bids_text = ""

        # шукаємо число перед словом "ставка/ставки/ставок"
        match = re.search(r"(\d+)\s+став", bids_text)
        if match:
            return int(match.group(1))
        return 0


    def extract_price(self, row: WebElement) -> int:
        try:
            price_text = row.find_element(*ProjectsSelector.PRICE).text.strip()
            price, currency = price_text.split()
            return int(price) * settings.ALLOWED_CURRENCIES[currency]
        except Exception as e:
            logger.exception(f"Failed to extract price")
            return settings.DEFAULT_PRICE_UAH

    def save_projects_to_db(self, page: int = 1) -> None:
        self.driver.get(f"{settings.FREELANCEHUNT_PROJECTS_PAGE}&page={page}")

        jobs = []
        rows = self.driver.find_elements(*ProjectsSelector.ALL_PROJECTS)

        for row in rows:
            try:
                title_el = row.find_element(*ProjectsSelector.TITLE)
                title = title_el.text.strip()
                link = title_el.get_attribute("href")

                if get_project(link):
                    continue

                # Можна щось перевіряти, але в бд не зберігати, бо дані дуже швидко стають неактуальними
                bids = self.extract_bids(row)

                jobs.append(CreateProjectSchema(
                    title=title,
                    link=link,
                    price=self.extract_price(row)
                ))

            except Exception as e:
                logger.exception(f"Failed to parse project: {e}")

        create_projects(jobs)

    
    def parse_project(self, project: Project) -> bool:
        self.driver.get(project.link)

        if self.driver.find_element(*ProjectSelector.TOO_MANY_BIDS):
            raise ValueError("Too many bids")

        # get message
        description_el = self.driver.find_element(*ProjectSelector.DESCRIPTION)
        description = remove_markup(description_el.get_attribute("innerHTML"))

        prompt = BASE_PROMPT.format(project_description=description)
        message = AI.prompt_to_ai(prompt)

        if message == "false":
            update_project(project.id, UpdateProjectSchema(is_bid_skipped=True))            
            return False
        
        update_project(project.id, UpdateProjectSchema(bid_message=message))

        # click "Place bid"
        place_bid_button = self.driver.find_element(*ProjectSelector.PLACE_BID_BUTTON)
        place_bid_button.click()

        # fill message
        message_input = self.driver.find_element(*ProjectSelector.MESSAGE_INPUT)
        message_input.send_keys(message)

        # fill days
        days_input = self.driver.find_element(*ProjectSelector.DAYS_INPUT)
        days_input.send_keys(settings.DEFAULT_DAYS)

        # fill price
        price_input = self.driver.find_element(*ProjectSelector.PRICE_INPUT)
        price_input.send_keys(project.price)

        # click "Place bid"
        place_bid_button = self.driver.find_element(*ProjectSelector.SUBMIT_BID_BUTTON)
        place_bid_button.click()

        update_project(project.id, UpdateProjectSchema(is_bid_placed=True))
        return True


