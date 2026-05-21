from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://report_user:report_pass@localhost:5432/report_db"
    service_name: str = "report-service"
    log_level: str = "INFO"
    # Shared secret used to authenticate calls from internal services.
    # Must be set to a strong random value in production via INTERNAL_API_KEY env var.
    internal_api_key: str = "dev-internal-api-key-change-in-production"

    model_config = {"env_file": ".env"}


settings = Settings()
