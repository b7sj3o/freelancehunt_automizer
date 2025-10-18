from drivers.browser import Browser
from auth.freelancehunt import Login as FreelanceHuntLogin
from auth.freelancer import Login as FreelancerLogin

class Authenticator:
    def __init__(self, browser: Browser):
        self.browser = browser
        self.freelancehunt = FreelanceHuntLogin(self.browser)
        self.freelancer = FreelancerLogin(self.browser)
    