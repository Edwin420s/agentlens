from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    mongo_uri: str = Field(default="mongodb://localhost:27017", alias="MONGO_URI")
    mongo_db_name: str = Field(default="agentlens", alias="MONGO_DB_NAME")

    ai_provider: str = Field(default="groq", alias="AI_PROVIDER")
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", alias="GROQ_MODEL")
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-1.5-flash", alias="GEMINI_MODEL")

    ai_max_retries: int = Field(default=3, alias="AI_MAX_RETRIES")
    ai_timeout_seconds: int = Field(default=45, alias="AI_TIMEOUT_SECONDS")


@lru_cache
def get_settings() -> Settings:
    return Settings()
