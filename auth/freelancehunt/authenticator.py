"""Freelancehunt authentication implementation."""
from core.config import settings
from core.browser import Browser
from auth.base import AuthenticatorFactory
from auth.freelancehunt.selectors import LoginPageSelectors, MFASelectors


class FreelanceHuntAuthenticator(AuthenticatorFactory):
    """Freelancehunt authenticator."""
    
    # Class attributes
    REQUIRES_MFA = True
    LOGIN_SELECTORS = LoginPageSelectors
    MFA_SELECTORS = MFASelectors
    
    def __init__(self, browser: Browser):
        """Initialize Freelancehunt authenticator.
        
        Args:
            browser: Browser instance
        """
        super().__init__(browser)
    
    def get_login_url(self) -> str:
        """Get Freelancehunt login URL."""
        return settings.FREELANCEHUNT_LOGIN_PAGE
    
    def get_credentials(self) -> tuple[str, str]:
        """Get Freelancehunt credentials.
        
        Returns:
            Tuple of (email, password)
        """
        return (settings.FREELANCEHUNT_EMAIL, settings.FREELANCEHUNT_PASSWORD)
