from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Google OAuth + GDrive
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/callback"

    # Gemini / Google AI (shared — backend only, never sent to mobile)
    GOOGLE_GENAI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Vertex AI Agent Builder (GenAI App Builder)
    GOOGLE_CLOUD_PROJECT: str = ""
    VERTEX_AI_LOCATION: str = "us-central1"
    VERTEX_AI_RAG_CORPUS: str = ""  # resource name, created on first run

    # GCP service account credentials
    GOOGLE_APPLICATION_CREDENTIALS: str = ""

    # GDrive
    GDRIVE_ROOT_FOLDER_NAME: str = "co-scienza"
    GDRIVE_ROOT_FOLDER_ID: str = ""  # filled on first run

    # Celery / Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # App
    SECRET_KEY: str = "change-me-in-production"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/coscienza.db"
    DATA_DIR: str = "./data"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
