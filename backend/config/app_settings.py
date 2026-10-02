from pydantic_settings import BaseSettings

from config.env import settings_config


class AppSettings(BaseSettings):
    environment: str = "development"

    model_config = settings_config()

    @property
    def is_production(self) -> bool:
        return self.environment.strip().lower() == "production"
