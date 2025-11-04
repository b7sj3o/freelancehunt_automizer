"""Freelancer.com authentication implementation."""
from core.config import settings
from core.browser import Browser
from auth.base import AuthenticatorFactory
from auth.freelancer.selectors import LoginPageSelectors


class FreelancerAuthenticator(AuthenticatorFactory):
    """Freelancer.com authenticator."""
    
    # Class attributes
    REQUIRES_MFA = False
    LOGIN_SELECTORS = LoginPageSelectors
    MFA_SELECTORS = None
    
    def __init__(self, browser: Browser):
        """Initialize Freelancer authenticator.
        
        Args:
            browser: Browser instance
        """
        super().__init__(browser)
    
    def get_login_url(self) -> str:
        """Get Freelancer login URL."""
        return settings.FREELANCER_LOGIN_PAGE
    
    def get_credentials(self) -> tuple[str, str]:
        """Get Freelancer credentials.
        
        Returns:
            Tuple of (email, password)
        """
        return (settings.FREELANCER_EMAIL, settings.FREELANCER_PASSWORD)

