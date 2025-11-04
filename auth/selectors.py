from selenium.webdriver.common.by import By
from abc import ABC

class LoginPageSelectorsFactory(ABC):
    EMAIL_INPUT: tuple[By, str]
    PASSWORD_INPUT: tuple[By, str]
    LOGIN_BUTTON: tuple[By, str]

class MFASelectorsFactory(ABC):
    MFA_INPUT: tuple[By, str]
    MFA_BUTTON: tuple[By, str]
    ERROR_ALERT: tuple[By, str]