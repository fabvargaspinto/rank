from config.db_settings import DBSettings


def get_supabase_url() -> str:
    return DBSettings().supabase_url.rstrip("/")
