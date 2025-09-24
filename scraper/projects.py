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


    def extract_price(self, row: WebElement) -> tuple[int, str]:
        try:
            price_text = row.find_element(*ProjectsSelector.PRICE).get_attribute("innerHTML").strip()
            *prices, currency = price_text.split()
            price = "".join(prices)
            return int(price), currency
        except Exception as e:
            return settings.DEFAULT_PRICE_UAH, "UAH"

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
                # bids = self.extract_bids(row)

                price, currency = self.extract_price(row)

                jobs.append(CreateProjectSchema(
                    title=title,
                    link=link,
                    price=price,
                    currency=currency
                ))

            except Exception as e:
                logger.error(f"Failed to parse project: {e}")

        create_projects(jobs)

    
    def parse_project(self, project: Project) -> bool:
        self.driver.get(project.link)

        # Alert "No more bids"
        try:
            self.driver.find_element(*ProjectSelector.NO_MORE_BIDS)
            update_project(project.id, UpdateProjectSchema(is_bid_skipped=True))
            return False
        except Exception as e:
            pass

        # Alert "Too many bids"
        try:
            self.driver.find_element(*ProjectSelector.TOO_MANY_BIDS)
            raise ValueError("Too many bids")
        except Exception as e:
            pass

        # Alert "Already bid"
        try:
            self.driver.find_element(*ProjectSelector.ALREADY_BID)
            update_project(project.id, UpdateProjectSchema(is_bid_placed=True))
            return True
        except Exception as e:
            pass

        try:
            # get message
            description_el = self.driver.find_element(*ProjectSelector.DESCRIPTION)
            description = remove_markup(description_el.get_attribute("innerHTML"))

            prompt = BASE_PROMPT.format(project_description=description)
            message = AI.prompt_to_ai(prompt)

            # ! Якщо None, то AI далбайоб вернув пусту строку 3 рази підряд і некст тайм коли я запущу код, ця вакансія ще раз піде до AI
            if not message:
                return False

            if message == "false":
                update_project(project.id, UpdateProjectSchema(is_bid_skipped=True))            
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
            price_input.send_keys(project.price)

            # click "Place bid"
            place_bid_button = self.driver.find_element(*ProjectSelector.SUBMIT_BID_BUTTON)
            place_bid_button.click()

            # Alert "Error"
            try:
                self.driver.find_element(*ProjectSelector.ERROR_ALERT)
                error_texts = self.driver.find_elements(*ProjectSelector.ERROR_TEXT)
                error_text = "\n".join([text.text for text in error_texts])
                logger.error(f"Errors: {error_text}")

                # ! треба мб перевірити можливі помилки
                return False
            except Exception as e:
                pass

            update_project(project.id, UpdateProjectSchema(bid_message=message, is_bid_placed=True))
            return True
        except:
            logger.exception("500 error")
            # Хз, будемо скіпати якщо ще якась помилка, бо заєбало вже
            update_project(project.id, UpdateProjectSchema(is_bid_skipped=True))
            return False


