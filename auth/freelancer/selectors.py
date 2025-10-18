from selenium.webdriver.common.by import By

class LoginPageSelectors:
    EMAIL_INPUT = (By.ID, "emailOrUsernameInput")
    PASSWORD_INPUT = (By.ID, "passwordInput")
    LOGIN_BUTTON = (By.XPATH, "//button[normalize-space(text())='Log in']")

