import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./youtuber_predictor.db")

settings = Settings()
