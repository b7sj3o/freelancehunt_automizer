import time
from config.settings import settings
from auth.selectors import LoginPageSelectors, MFASelectors
from drivers.browser import Browser

class Login:
    def __init__(self, browser: Browser):
        self.browser = browser

    def submit_mfa_code(self, max_tries: int = 3) -> bool:
        if max_tries == 0:
            print("Max tries reached\n")
            return False

        mfa_code = input("Enter MFA code: ")

        if not mfa_code or len(mfa_code) != 6 or not mfa_code.isdigit():
            print("Invalid MFA code format\n")
            return self.submit_mfa_code(max_tries-1)

        mfa_input = self.browser.wait_until(MFASelectors.MFA_INPUT)
        mfa_input.send_keys(mfa_code)

        mfa_button = self.browser.wait_until(MFASelectors.MFA_BUTTON)
        mfa_button.click()

        time.sleep(1)

        try:
            self.browser.wait_until(MFASelectors.ERROR_ALERT, timeout=2)
            print("Invalid MFA code\n")
            return self.submit_mfa_code(max_tries-1)
        except:
            pass

        return True

    # TODO: handle error "login or password incorrect"
    def login(self) -> None:
        self.browser.driver.get(settings.FREELANCEHUNT_LOGIN_PAGE)

        email_input = self.browser.wait_until(LoginPageSelectors.EMAIL_INPUT)
        password_input = self.browser.wait_until(LoginPageSelectors.PASSWORD_INPUT)
        email_input.send_keys(settings.FREELANCEHUNT_EMAIL)
        password_input.send_keys(settings.FREELANCEHUNT_PASSWORD)
        
        login_button = self.browser.wait_until(LoginPageSelectors.LOGIN_BUTTON)
        login_button.click()

        if not self.submit_mfa_code():
            raise Exception("Failed to login")

    