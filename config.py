import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database configuration
    # POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    # POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    # POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_agent_db")
    # POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    # POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", 5432))

    # LLM credentials (for real usage with OpenAI or other providers)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    class Config:
        env_file = ".env"
