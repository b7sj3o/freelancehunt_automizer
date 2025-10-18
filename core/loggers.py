from core.logger_config import setup_logger


ai_logger = setup_logger(name="ai", log_file="ai.log")
browser_logger = setup_logger(name="browser", log_file="browser.log")
login_logger = setup_logger(name="login", log_file="login.log")
db_logger = setup_logger(name="db", log_file="db.log")
gui_logger = setup_logger(name="gui", log_file="gui.log")
requests_logger = setup_logger(name="requests", log_file="requests.log")
freelancehunt_logger = setup_logger(name="freelancehunt", log_file="freelancehunt.log")
freelancer_logger = setup_logger(name="freelancer", log_file="freelancer_projects_scraper.log")
projects_scraper_logger = setup_logger(name="projects_scraper", log_file="projects_scraper.log")
