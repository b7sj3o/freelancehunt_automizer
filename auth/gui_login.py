"""GUI-specific authentication implementation."""
from typing import Callable

from core.config import settings
from drivers.browser import Browser
from auth.base import BaseAuthenticator
from auth.freelancehunt.selectors import LoginPageSelectors, MFASelectors


class GUILogin(BaseAuthenticator):
    """GUI authenticator for Freelancehunt with callback for MFA."""
    
    # Class attributes
    REQUIRES_MFA = True
    LOGIN_SELECTORS = LoginPageSelectors
    MFA_SELECTORS = MFASelectors
    
    def __init__(self, browser: Browser, mfa_callback: Callable[[], str]):
        """Initialize GUI authenticator.
        
        Args:
            browser: Browser instance
            mfa_callback: Callback function to get MFA code from GUI
        """
        super().__init__(browser, mfa_callback)
    
    def get_login_url(self) -> str:
        """Get Freelancehunt login URL."""
        return settings.FREELANCEHUNT_LOGIN_PAGE
    
    def get_credentials(self) -> tuple[str, str]:
        """Get Freelancehunt credentials.
        
        Returns:
            Tuple of (email, password)
        """
        return (settings.FREELANCEHUNT_EMAIL, settings.FREELANCEHUNT_PASSWORD)
