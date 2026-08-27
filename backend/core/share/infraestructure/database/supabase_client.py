import threading

from supabase import Client, create_client

from config.db_config import DBConfig
from core.share.infraestructure.infra_error import DatabaseError


class SupabaseClient:
    _instance: "SupabaseClient | None" = None
    _lock = threading.Lock()

    def __new__(
        cls,
        config: DBConfig | None = None,
    ) -> "SupabaseClient":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialize(config)
                    cls._instance = instance

        return cls._instance

    def _initialize(self, config: DBConfig | None) -> None:
        resolved_config = config or DBConfig()
        self._url = resolved_config.url.strip()
        self._client = self._create_client(resolved_config)

    @staticmethod
    def _create_client(config: DBConfig) -> Client:
        url = config.url.strip()
        secret_key = config.secret_key.strip()

        if not url:
            raise DatabaseError("Supabase URL is empty")

        if not secret_key:
            raise DatabaseError("Supabase secret key is empty")

        try:
            return create_client(
                url,
                secret_key,
            )
        except Exception as error:
            raise DatabaseError(
                "Failed to create Supabase client"
            ) from error

    def get_client(self) -> Client:
        return self._client

    def check_connection(self) -> None:
        try:
            response = self._client.postgrest.session.get(
                f"{self._url.rstrip('/')}/rest/v1/",
            )
            response.raise_for_status()
        except Exception as error:
            raise DatabaseError("Database is unavailable") from error