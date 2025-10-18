from selenium.webdriver.common.by import By

class LoginPageSelectors:
    EMAIL_INPUT: tuple[By, str]
    PASSWORD_INPUT: tuple[By, str]
    LOGIN_BUTTON: tuple[By, str]

class MFASelectors:
    MFA_INPUT: tuple[By, str]
    MFA_BUTTON: tuple[By, str]
    ERROR_ALERT: tuple[By, str]