from auth.base import AuthenticatorFactory
from auth.freelancehunt import FreelanceHuntAuthenticator
from auth.freelancer import FreelancerAuthenticator
from schemas.project import MarketplaceEnum

AUTHENTICATORS = {
    MarketplaceEnum.FREELANCEHUNT: FreelanceHuntAuthenticator,
    MarketplaceEnum.FREELANCER: FreelancerAuthenticator,
}

def get_authenticator(marketplace: MarketplaceEnum, browser) -> AuthenticatorFactory:
    authenticator_class = AUTHENTICATORS.get(marketplace)
    if not authenticator_class:
        raise ValueError(f"Unknown marketplace: {marketplace}")
    return authenticator_class(browser)