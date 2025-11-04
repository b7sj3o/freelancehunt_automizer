"""Base authentication interface and common logic."""
import time
from abc import ABC, abstractmethod
from typing import Optional, Callable
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from auth.selectors import LoginPageSelectorsFactory, MFASelectorsFactory
from core.exceptions import (
    LoginFailedError,
    MFARequiredError,
    InvalidCredentialsError,
)
from core.browser import Browser
from core.loggers import login_logger as logger


class AuthenticatorFactory(ABC):
    """Base authenticator with common authentication logic."""
    
    # Class attributes - override in subclasses
    REQUIRES_MFA: bool = True
    LOGIN_SELECTORS: LoginPageSelectorsFactory
    MFA_SELECTORS: Optional[MFASelectorsFactory]
    
    def __init__(self, browser: Browser, mfa_callback: Optional[Callable[[], str]] = None):
        """Initialize authenticator.
        
        Args:
            browser: Browser instance
            mfa_callback: Optional callback function to get MFA code (for GUI mode)
        """
        self.browser = browser
        self.mfa_callback = mfa_callback
    
    @property
    def requires_mfa(self) -> bool:
        """Check if this marketplace requires MFA.
        
        Returns:
            True if MFA is required for this marketplace
        """
        return self.REQUIRES_MFA
    
    @abstractmethod
    def get_login_url(self) -> str:
        """Get login page URL for specific marketplace.
        
        Returns:
            Login page URL
        """
        pass
    
    @abstractmethod
    def get_credentials(self) -> tuple[str, str]:
        """Get email and password for specific marketplace.
        
        Returns:
            Tuple of (email, password)
        """
        pass


    def _get_mfa_code_from_input(self) -> Optional[str]:
        """Get MFA code from console input.
        
        Returns:
            MFA code or None if invalid
        """
        mfa_code = input("Enter 6-digit MFA code: ").strip()
        
        if not mfa_code:
            return None
        
        if len(mfa_code) != 6 or not mfa_code.isdigit():
            logger.warning("Invalid MFA code format. Must be 6 digits.")
            return None
        
        return mfa_code
    
    def _check_mfa_required(self) -> bool:
        """Check if MFA is required.
        
        Returns:
            True if MFA input is present on page
        """
        # If marketplace doesn't support MFA, skip check
        if not self.requires_mfa:
            logger.info("MFA not supported for this marketplace")
            return False
        
        if self.MFA_SELECTORS is None:
            logger.info("MFA selectors not configured")
            return False
        
        try:
            self.browser.wait_until(self.MFA_SELECTORS.MFA_INPUT, timeout=3)
            return True
        except (TimeoutException, NoSuchElementException):
            return False
    
    def _submit_mfa_code(self, max_tries: int = 3) -> bool:
        """Submit MFA code with retries.
        
        Args:
            max_tries: Maximum number of attempts
            
        Returns:
            True if MFA was successful
            
        Raises:
            MFARequiredError: If MFA is required but cannot be completed
        """
        if not self._check_mfa_required():
            logger.info("MFA not required")
            return True
        
        logger.info("MFA required")
        
        for attempt in range(1, max_tries + 1):
            logger.info(f"MFA attempt {attempt}/{max_tries}")
            
            # Get MFA code
            mfa_code = None
            if self.mfa_callback:
                mfa_code = self.mfa_callback()
            else:
                mfa_code = self._get_mfa_code_from_input()
            
            if not mfa_code:
                logger.warning("No MFA code provided")
                if attempt < max_tries:
                    continue
                else:
                    raise MFARequiredError("MFA code required but not provided")
            
            # Validate format
            if len(mfa_code) != 6 or not mfa_code.isdigit():
                logger.warning(f"Invalid MFA code format: {mfa_code}")
                if attempt < max_tries:
                    continue
                else:
                    raise MFARequiredError("Invalid MFA code format")
            
            # Submit MFA code
            try:
                mfa_input = self.browser.wait_until(self.MFA_SELECTORS.MFA_INPUT)
                mfa_input.clear()
                mfa_input.send_keys(mfa_code)
                
                mfa_button = self.browser.wait_until(self.MFA_SELECTORS.MFA_BUTTON)
                mfa_button.click()
                
                logger.info("MFA code submitted")
                time.sleep(2)  # Wait for processing
                
                # Check for error
                try:
                    self.browser.wait_until(self.MFA_SELECTORS.ERROR_ALERT, timeout=2)
                    logger.warning("Invalid MFA code")
                    if attempt < max_tries:
                        continue
                    else:
                        raise MFARequiredError("Invalid MFA code - max tries exceeded")
                except TimeoutException:
                    # No error - success!
                    logger.info("MFA successful")
                    return True
                    
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"Error submitting MFA: {e}")
                if attempt < max_tries:
                    continue
                else:
                    raise MFARequiredError(f"Failed to submit MFA: {e}") from e
        
        return False
    
    def _check_login_error(self) -> None:
        """Check for login errors on page.
        
        Raises:
            InvalidCredentialsError: If credentials are invalid
        """
        try:
            # Check for error message (можна додати селектори)
            # TODO: Add proper error selectors for each marketplace
            pass
        except Exception:
            pass
    
    def login(self) -> bool:
        """Perform login with credentials and optional MFA.
        
        Returns:
            True if login successful
            
        Raises:
            LoginFailedError: If login fails
            InvalidCredentialsError: If credentials are invalid
            MFARequiredError: If MFA cannot be completed
        """
        try:
            # Get credentials
            email, password = self.get_credentials()
            login_url = self.get_login_url()
            
            logger.info(f"Starting login to {login_url}")
            
            # Navigate to login page
            self.browser.driver.get(login_url)
            logger.info("Login page loaded")
            
            # Enter credentials
            try:
                email_input = self.browser.wait_until(self.LOGIN_SELECTORS.EMAIL_INPUT)
                password_input = self.browser.wait_until(self.LOGIN_SELECTORS.PASSWORD_INPUT)
                
                email_input.clear()
                email_input.send_keys(email)
                
                password_input.clear()
                password_input.send_keys(password)
                
                logger.info("Credentials entered")
                
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"Failed to find login form elements: {e}")
                raise LoginFailedError("Login form not found") from e
            
            # Click login button
            try:
                login_button = self.browser.wait_until(self.LOGIN_SELECTORS.LOGIN_BUTTON)
                login_button.click()
                logger.info("Login button clicked")
                
                time.sleep(2)  # Wait for redirect
                
            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"Failed to click login button: {e}")
                raise LoginFailedError("Login button not found") from e
            
            # Check for credential errors
            self._check_login_error()
            
            # Handle MFA if required
            mfa_success = self._submit_mfa_code()
            
            if mfa_success:
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed - MFA not completed")
                raise LoginFailedError("MFA verification failed")
                
        except (MFARequiredError, InvalidCredentialsError):
            # Re-raise specific errors
            raise
            
        except Exception as e:
            logger.error(f"Login failed with unexpected error: {e}", exc_info=True)
            raise LoginFailedError(f"Login failed: {e}") from e

