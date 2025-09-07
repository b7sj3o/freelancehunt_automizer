import time

from db import Base, engine
from db.requests import get_active_projects
from auth.login import Login
from drivers.browser import Browser
from scraper.projects import ProjectsScraper
from core.logger_config import setup_logger

logger = setup_logger(name="main", log_file="main.log")

class Main:
    def __init__(self):
        self.browser = Browser()
        self.login = Login(self.browser)
        self.projects_scraper = ProjectsScraper(self.browser)

        Base.metadata.create_all(bind=engine)

    def run(self): 
        self.login.login()

        def get_pages_range(tries: int = 5) -> tuple:
            if tries == 0:
                raise ValueError("All tries were exceeded")
            pages = input("Enter amount of pages you want to parse (to) or (from,to)")

            # TODO: handle .split()[1] error and others
            
            if pages.isdigit():
                return (1, int(pages)+1)

            n_from, n_to = pages.split(",")
            if n_from.isdigit() and n_to.isdigit():
                return (int(n_from), int(n_to)+1)
            else:
                return get_pages_range(tries-1)

        # Тут просто зберігаємо в бд
        for page in range(*get_pages_range()):
            self.projects_scraper.save_projects_to_db(page)

        # Тут парсимо вже з бд всі, що не мають ставки
        projects = get_active_projects()
        for project in projects:
            is_bid_placed = self.projects_scraper.parse_project(project)

            if is_bid_placed:
                print(f"Bid placed for {project.link}")
            else:
                print(f"bid was not placed for {project.link}")

        time.sleep(5)

        logger.info("All projects were parsed and saved to db")


if __name__ == "__main__":
    main = Main()
    main.run()