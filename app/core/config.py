from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/webhook_service")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Application
    APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "your-secret-key-here")
    LOG_RETENTION_HOURS: int = int(os.getenv("LOG_RETENTION_HOURS", "72"))
    MAX_RETRY_ATTEMPTS: int = int(os.getenv("MAX_RETRY_ATTEMPTS", "5"))
    
    # Celery
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 