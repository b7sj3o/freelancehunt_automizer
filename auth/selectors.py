from selenium.webdriver.common.by import By

class LoginPageSelectors:
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='text'].form-control")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password'].form-control")
    LOGIN_BUTTON = (By.CSS_SELECTOR, "button.btn-auth")

class MFASelectors:
    MFA_INPUT = (By.CLASS_NAME, "form-control")
    MFA_BUTTON = (By.CLASS_NAME, "ladda-button")
    ERROR_ALERT = (By.CLASS_NAME, "alert-error")