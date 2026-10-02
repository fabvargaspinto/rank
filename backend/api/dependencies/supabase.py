from functools import lru_cache

from config.db_settings import DBSettings


@lru_cache
def get_supabase_url() -> str:
    return DBSettings().supabase_url.rstrip("/")  # type: ignore[call-arg]
