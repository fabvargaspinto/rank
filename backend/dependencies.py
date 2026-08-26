from typing import Annotated

from fastapi import Depends, Request

from config.app_config import AppConfig
from config.crypto_config import CryptoConfig
from config.db_config import DBConfig
from domain.Auth.email_protector import EmailProtector
from infrastructure.database.supabase_client import SupabaseClient


def get_app_config(request: Request) -> AppConfig:
    return request.app.state.app_config


def get_db_config(request: Request) -> DBConfig:
    return request.app.state.db_config


def get_crypto_config(request: Request) -> CryptoConfig:
    return request.app.state.crypto_config


def get_supabase_client(request: Request) -> SupabaseClient:
    return request.app.state.supabase_client


def get_email_protector(request: Request) -> EmailProtector:
    return request.app.state.email_protector


AppConfigDep = Annotated[AppConfig, Depends(get_app_config)]
DBConfigDep = Annotated[DBConfig, Depends(get_db_config)]
CryptoConfigDep = Annotated[CryptoConfig, Depends(get_crypto_config)]
SupabaseClientDep = Annotated[SupabaseClient, Depends(get_supabase_client)]
EmailProtectorDep = Annotated[EmailProtector, Depends(get_email_protector)]
