from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Autonomous API Builder"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/autonomous_api_builder"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
