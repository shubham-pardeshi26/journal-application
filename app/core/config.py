# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from decouple import config as envCreds

class Settings(BaseSettings):
    # Model configuration for environment variables
    # looks for .env file in the directory where the application is run
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Database Settings ---
    DATABASE_URL: str = envCreds("DB_URL") # Default to SQLite for easy local dev

    # --- Security Settings ---
    SECRET_KEY: str = envCreds("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # Optional, if you implement refresh tokens
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 60
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Email Settings ---
    # These are examples. Adjust based on your actual email service (SMTP, SendGrid, Mailgun etc.)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: str = "Your Journaling App"

    # --- Project Settings ---
    PROJECT_NAME: str = "Journaling App Backend"
    API_V1_STR: str = "/api/v1" # Base path for API version 1
    # Add any other settings you might need, e.g., for file storage (S3 bucket details)
    # AWS_ACCESS_KEY_ID: Optional[str] = None
    # AWS_SECRET_ACCESS_KEY: Optional[str] = None
    # AWS_REGION: Optional[str] = None
    # S3_BUCKET_NAME: Optional[str] = None

settings = Settings()