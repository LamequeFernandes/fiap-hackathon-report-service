from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://report_user:report_pass@localhost:5432/report_db"
    service_name: str = "report-service"
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}


settings = Settings()
