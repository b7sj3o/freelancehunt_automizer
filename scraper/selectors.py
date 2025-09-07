from selenium.webdriver.common.by import By

class ProjectsSelector:
    ALL_PROJECTS = (By.XPATH, "//tbody/tr")

    TITLE = (By.XPATH, ".//a[contains(@class,'visitable')]")
    BIDS = (By.XPATH, ".//*[self::span or self::small][contains(., 'став')]")
    PRICE = (By.XPATH, ".//div[contains(@class,'price')]")


class ProjectSelector:
    DESCRIPTION = (By.ID, "project-description")
    PLACE_BID_BUTTON = (By.ID, "add-bid")
    PROJECT_PRICE = (By.XPATH, "//span[contains(@class, 'text-green') and contains(@class, 'price')]")

    MESSAGE_INPUT = (By.ID, "comment-0")
    DAYS_INPUT = (By.ID, "days_to_deliver-0")
    PRICE_INPUT = (By.ID, "amount-0")
    SUBMIT_BID_BUTTON = (
        By.XPATH,
        "//button[@id='add-0' or @id='btn-submit-0']"
    )

    TOO_MANY_BIDS = (By.XPATH, "//*[contains(@class, 'alert-info') and contains(., 'Ви додали занадто багато ставок за останню добу, почекайте трохи перед додаванням нової ставки.')]")

    # ALREADY_BID = (By.CLASS_NAME, "alert-info")
    # ALREADY_BID = (By.XPATH, "//*[contains(@class, 'alert-info') and contains(., 'Ви вже зробили ставку на цей проєкт')]")





    