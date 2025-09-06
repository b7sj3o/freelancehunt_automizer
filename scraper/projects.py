import re
import time

from selenium.common.exceptions import NoSuchElementException

from ai.prompts import BASE_PROMPT
from core.config import settings
from drivers.browser import Browser
from schemas.project import ProjectSchema
from scraper.selectors import ProjectsSelector, ProjectSelector
from utils.helpers import remove_markup
from ai.client import AI

class ProjectsScraper:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.driver = browser.driver

        if not self.driver:
            raise ValueError("Driver is not initialized")


    def extract_bids(self, row):
        try:
            bids_text = row.find_element(*ProjectsSelector.BIDS).text
        except:
            bids_text = ""

        # шукаємо число перед словом "ставка/ставки/ставок"
        match = re.search(r"(\d+)\s+став", bids_text)
        if match:
            return int(match.group(1))
        return 0



    def parse_projects(self, page: int = 1) -> list[ProjectSchema]:
        self.driver.get(f"{settings.FREELANCEHUNT_PROJECTS_PAGE}&page={page}")

        jobs = []
        rows = self.driver.find_elements(*ProjectsSelector.ALL_PROJECTS)

        for row in rows:
            try:
                title_el = row.find_element(*ProjectsSelector.TITLE)
                title = title_el.text.strip()
                link = title_el.get_attribute("href")

                jobs.append(ProjectSchema(
                    title=title,
                    link=link,
                    bids=self.extract_bids(row)
                ))

            except Exception as e:
                print(f"Failed to parse project: {e}")

        return jobs

    
    def parse_project(self, link: str) -> bool:
        self.driver.get(link)

        try:
            self.driver.find_element(*ProjectSelector.ALREADY_BID)
            return False
        except NoSuchElementException:
            pass

        # get project price
        try:
            price_text = self.driver.find_element(*ProjectSelector.PROJECT_PRICE).text
            price_int = int("".join(filter(str.isdigit, price_text)))
        except NoSuchElementException:
            price_int = settings.DEFAULT_PRICE

        # get message
        description_el = self.driver.find_element(*ProjectSelector.DESCRIPTION)
        description = remove_markup(description_el.get_attribute("innerHTML"))

        prompt = BASE_PROMPT.format(project_description=description)
        message = AI.prompt_to_ai(prompt)

        if message == "false":
            return False
        
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
        price_input.send_keys(price_int)

        # click "Place bid"
        place_bid_button = self.driver.find_element(*ProjectSelector.SUBMIT_BID_BUTTON)
        place_bid_button.click()

        return True


