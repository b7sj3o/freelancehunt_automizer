import time
from drivers.browser import Browser
from scraper.selectors import ProjectsSelector
from core.config import settings
from selenium.webdriver.remote.webelement import WebElement
from auth.login import Login


def extract_price(row: WebElement) -> int:
    try:
        price_text = row.find_element(*ProjectsSelector.PRICE).get_attribute("innerHTML").strip()
        *prices, currency = price_text.split()
        price = "".join(prices)
        return int(price), currency
    except Exception as e:
        return "default"



def get_projects():
    return browser.driver.find_elements(*ProjectsSelector.ALL_PROJECTS)


if __name__ == "__main__":
    
    url = "https://freelancehunt.com/projects?skills%5B%5D=124&skills%5B%5D=28&skills%5B%5D=99"
    browser = Browser()
    
    login = Login(browser)
    login.login()

    for i in range(1, 10):
        browser.driver.get(f"{url}&page={i}")

        projects = get_projects()

        for project in projects:
            extract_price(project)


    time.sleep(1000)