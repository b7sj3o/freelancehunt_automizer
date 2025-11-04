import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class Settings:
    def __init__(self):
        self.DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
        self.IS_DOCKER: bool = os.getenv("IS_DOCKER", "false").lower() == "true"

        # Database
        self.DATABASE_URL: str = os.getenv("DATABASE_URL") if not self.IS_DOCKER else os.getenv("DOCKER_DATABASE_URL")

        # Freelancehunt pages
        self.FREELANCEHUNT_LOGIN_PAGE: str = os.getenv("FREELANCEHUNT_LOGIN_PAGE")
        self.FREELANCEHUNT_PROJECTS_PAGE: str = os.getenv("FREELANCEHUNT_PROJECTS_PAGE")

        # Freelancehunt credentials
        self.FREELANCEHUNT_EMAIL: str = os.getenv("FREELANCEHUNT_EMAIL")
        self.FREELANCEHUNT_PASSWORD: str = os.getenv("FREELANCEHUNT_PASSWORD")

        # Freelancer credentials
        self.FREELANCER_LOGIN_PAGE = os.getenv("FREELANCER_LOGIN_PAGE")
        self.FREELANCER_PROJECTS_PAGE: str = os.getenv("FREELANCER_PROJECTS_PAGE")
        self.FREELANCER_EMAIL: str = os.getenv("FREELANCER_EMAIL")
        self.FREELANCER_PASSWORD: str = os.getenv("FREELANCER_PASSWORD")


        # Default values
        self.DEFAULT_DAYS: int = int(os.getenv("DEFAULT_DAYS", 1))
        self.DEFAULT_PRICE_UAH: int = int(os.getenv("DEFAULT_PRICE_UAH", 5000))

        # Selenium settings
        self.CHROMEDRIVER_PATH: str = os.getenv("CHROMEDRIVER_PATH") if not self.IS_DOCKER else os.getenv("DOCKER_CHROMEDRIVER_PATH")

        # OpenRouter settings
        self.OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
        self.OPENROUTER_AI_MODEL: str = os.getenv("OPENROUTER_AI_MODEL")
        
        # AI settings
        self.AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", 0.5))
        self.AI_TOP_P: float = float(os.getenv("AI_TOP_P", 1))
        self.AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", 1000))
        self.AI_SYSTEM_CONTENT: str = os.getenv("AI_SYSTEM_CONTENT")

        # Initialize client
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.OPENROUTER_API_KEY
        )

        self._validate_env()

    def _validate_env(self):

        missing_vars = [var_name for var_name, var_value in self.__dict__.items() if var_value is None]

        if missing_vars:
            raise EnvironmentError(f"Variable(s) {", ".join(missing_vars)} is/are missing. Check your .env file and IS_DOCKER value")


settings = Settings()