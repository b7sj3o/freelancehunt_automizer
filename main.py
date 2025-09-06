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
        # self.login.login()

        def get_pages(tries: int = 3) -> tuple:
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
                return get_pages(tries-1)

        for page in range(*get_pages()):
            projects = self.projects_scraper.parse_projects(page)

            for project in projects:
                is_bid_placed = self.projects_scraper.parse_project(project.link)

                if is_bid_placed:
                    print(f"Bid placed for {project.link}")
                else:
                    print(f"bid was not placed for {project.link}")

        time.sleep(1000)


if __name__ == "__main__":
    main = Main()
    main.run()