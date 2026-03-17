from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "Autonomous API Builder"
    app_env: str = "development"
    database_url: str = "postgresql+psycopg2://postgres:postgres@db:5432/autonomous_api_builder"
    queue_backend: str = "celery"
    redis_url: str = "redis://redis:6379/0"
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None
    planner_model: str = "gpt-4o-mini"
    planner_api_key: str | None = None
    planner_base_url: str = "https://api.openai.com/v1"
    planner_max_retries: int = 2
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    storage_backend: str = "local"
    storage_local_base_path: str = "./data/artifacts"
    otel_enabled: bool = False
    otel_service_name: str = "autonomous-api-builder-api"
    otel_exporter_otlp_endpoint: str = "http://otel-collector:4318/v1/traces"

    @property
    def effective_celery_broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def effective_celery_result_backend(self) -> str:
        return self.celery_result_backend or self.redis_url

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
