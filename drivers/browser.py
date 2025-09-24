from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

from core.config import settings
from core.logger_config import setup_logger

logger = setup_logger(name="browser", log_file="browser.log")

class Browser:
    def __init__(self):
        self.driver = webdriver.Chrome(service=self.get_service(), options=self.get_options())


    def get_service(self) -> Service:
        service = Service(executable_path=settings.CHROMEDRIVER_PATH)
        return service

    def get_options(self) -> Options:
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        return options

    def close_driver(self) -> None:
        if self.driver is not None:
            self.driver.quit()
            self.driver = None

    def wait_until(self, locator: tuple, timeout: int = 3) -> WebElement:
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
        except Exception as e:
            logger.error(f"Failed to wait until {locator}")
            raise e