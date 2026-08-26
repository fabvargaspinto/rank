from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from config.app_config import AppConfig
from config.crypto_config import CryptoConfig
from config.db_config import DBConfig
from infrastructure.crypto.fernet_email_protector import FernetEmailProtector
from infrastructure.database.supabase_client import SupabaseClient


def create_app(
    app_config: AppConfig | None = None,
    db_config: DBConfig | None = None,
    crypto_config: CryptoConfig | None = None,
    supabase_client: SupabaseClient | None = None,
    email_protector: FernetEmailProtector | None = None,
) -> FastAPI:
    resolved_app_config = app_config or AppConfig()
    resolved_db_config = db_config or DBConfig()
    resolved_crypto_config = crypto_config or CryptoConfig()
    resolved_supabase_client = supabase_client or SupabaseClient(
        resolved_db_config
    )
    resolved_email_protector = email_protector or FernetEmailProtector(
        resolved_crypto_config
    )

    app = FastAPI()
    app.state.app_config = resolved_app_config
    app.state.db_config = resolved_db_config
    app.state.crypto_config = resolved_crypto_config
    app.state.supabase_client = resolved_supabase_client
    app.state.email_protector = resolved_email_protector

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_app_config.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def read_root():
        return {"message": "Hello, World!"}

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
