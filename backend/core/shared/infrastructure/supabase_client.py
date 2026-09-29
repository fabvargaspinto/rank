from supabase import Client, ClientOptions, create_client

from config.db_settings import DBSettings


class DBClient:
    def __init__(self, db_settings: DBSettings):
        self._client: Client = create_client(
            db_settings.supabase_url,
            db_settings.supabase_secret_key,
            options=ClientOptions(
                auto_refresh_token=False,
                persist_session=False,
            ),
        )

    def get_db(self) -> Client:
        return self._client
