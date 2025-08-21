import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

class Settings:
    def __init__(self):
        # Freelancehunt pages
        self.FREELANCEHUNT_LOGIN_PAGE = os.getenv("FREELANCEHUNT_LOGIN_PAGE")
        self.FREELANCEHUNT_PROJECTS_PAGE = os.getenv("FREELANCEHUNT_PROJECTS_PAGE")

        # Freelancehunt credentials
        self.FREELANCEHUNT_EMAIL = os.getenv("FREELANCEHUNT_EMAIL")
        self.FREELANCEHUNT_PASSWORD = os.getenv("FREELANCEHUNT_PASSWORD")

        # Default values
        self.DEFAULT_DAYS = int(os.getenv("DEFAULT_DAYS"))
        self.DEFAULT_PRICE = int(os.getenv("DEFAULT_PRICE"))

        # Selenium settings
        self.CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")

        # OpenRouter settings
        self.OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY")
        self.OPENROUTER_AI_MODEL: str = os.getenv("OPENROUTER_AI_MODEL")
        
        # AI settings
        self.AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE"))
        self.AI_TOP_P: float = float(os.getenv("AI_TOP_P"))
        self.AI_MAX_TOKENS: int = int(os.getenv("AI_MAX_TOKENS"))
        self.AI_SYSTEM_CONTENT: str = os.getenv("AI_SYSTEM_CONTENT")

        # Initialize client
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.OPENROUTER_API_KEY
        )

settings = Settings()