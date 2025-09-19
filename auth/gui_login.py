import time
from core.config import settings
from auth.selectors import LoginPageSelectors, MFASelectors
from drivers.browser import Browser

class GUILogin:
    def __init__(self, browser: Browser, mfa_callback=None):
        self.browser = browser
        self.mfa_callback = mfa_callback  # Функція для отримання MFA коду від GUI

    def submit_mfa_code(self, max_tries: int = 3) -> bool:
        # Можливо 2-ох факторки немає, тому пропускаємо
        try:
            self.browser.wait_until(MFASelectors.MFA_INPUT, timeout=5)
        except Exception as e:
            return True  # MFA не потрібен
        
        if max_tries == 0:
            return False

        # Отримуємо код через GUI callback
        if self.mfa_callback:
            mfa_code = self.mfa_callback()
            if not mfa_code:  # Користувач скасував
                return False
        else:
            return False  # Немає способу отримати код

        if not mfa_code or len(mfa_code) != 6 or not mfa_code.isdigit():
            return self.submit_mfa_code(max_tries-1)

        try:
            mfa_input = self.browser.wait_until(MFASelectors.MFA_INPUT)
            mfa_input.clear()
            mfa_input.send_keys(mfa_code)

            mfa_button = self.browser.wait_until(MFASelectors.MFA_BUTTON)
            mfa_button.click()

            time.sleep(2)  # Даємо час на обробку

            # Перевіряємо на помилку
            try:
                self.browser.wait_until(MFASelectors.ERROR_ALERT, timeout=3)
                return self.submit_mfa_code(max_tries-1)  # Неправильний код, пробуємо знову
            except:
                pass  # Помилки немає, все добре

            return True
        except Exception as e:
            return self.submit_mfa_code(max_tries-1)

    def login(self) -> bool:
        try:
            self.browser.driver.get(settings.FREELANCEHUNT_LOGIN_PAGE)

            email_input = self.browser.wait_until(LoginPageSelectors.EMAIL_INPUT)
            password_input = self.browser.wait_until(LoginPageSelectors.PASSWORD_INPUT)
            email_input.clear()
            email_input.send_keys(settings.FREELANCEHUNT_EMAIL)
            password_input.clear()
            password_input.send_keys(settings.FREELANCEHUNT_PASSWORD)
            
            login_button = self.browser.wait_until(LoginPageSelectors.LOGIN_BUTTON)
            login_button.click()
            
            time.sleep(2)  # Даємо час на перенаправлення

            # Обробляємо MFA якщо потрібно
            return self.submit_mfa_code()
            
        except Exception as e:
            print(f"Login error: {e}")
            return False
