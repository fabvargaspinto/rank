from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() == "production"
