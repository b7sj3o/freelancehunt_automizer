import time

from drivers.browser import Browser
from scraper.projects import ProjectsScraper
from auth.login import Login

class Main:
    def __init__(self):
        self.browser = Browser()
        self.login = Login(self.browser)
        self.projects_scraper = ProjectsScraper(self.browser)

    def run(self): 
        self.login.login()

        projects = self.projects_scraper.parse_projects()
        for project in projects:
                is_bid_placed = self.projects_scraper.parse_project(project.link)

                if is_bid_placed:
                    print(f"Bid placed for {project.link}")
                else:
                    print(f"Already bid for {project.link}")
                
        

        time.sleep(1000)


if __name__ == "__main__":
    main = Main()
    main.run()