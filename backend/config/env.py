from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[2]


def is_production_env() -> bool:
    return os.environ.get("ENVIRONMENT", "development").strip().lower() == "production"


def repo_env_file() -> Path | None:
    """`.env` at the repo root for local/dev. Production uses the process env only."""
    if is_production_env():
        return None
    path = _REPO_ROOT / ".env"
    return path if path.is_file() else None


def settings_config(**extra: object) -> SettingsConfigDict:
    return SettingsConfigDict(
        env_file=repo_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
        **extra,
    )
