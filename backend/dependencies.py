from typing import Annotated

from fastapi import Depends, Request

from config.app_config import AppConfig
from config.crypto_config import CryptoConfig
from config.db_config import DBConfig
from core.auth.application.auth_strategy import GetStrategy
from core.auth.infraestructure.auth_supabase_repo import AuthSupabaseRepo
from core.auth.domain.email_protector import EmailProtector
from core.share.infraestructure.database.supabase_client import SupabaseClient
from core.user.infraestructure.user_supabase_repo import UserSupabaseRepo


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



def get_strategy_factory(request: Request) -> GetStrategy:
    return request.app.state.get_strategy

def get_auth_repo(request: Request) -> AuthSupabaseRepo:
    return request.app.state.auth_repo

def get_user_supabase_repo(request: Request) -> UserSupabaseRepo:
    return request.app.state.user_supabase_repo

AppConfigDep = Annotated[AppConfig, Depends(get_app_config)]
DBConfigDep = Annotated[DBConfig, Depends(get_db_config)]
CryptoConfigDep = Annotated[CryptoConfig, Depends(get_crypto_config)]
SupabaseClientDep = Annotated[SupabaseClient, Depends(get_supabase_client)]
EmailProtectorDep = Annotated[EmailProtector, Depends(get_email_protector)]
GetStrategyDep = Annotated[GetStrategy, Depends(get_strategy_factory)]
AuthRepoDep = Annotated[AuthSupabaseRepo, Depends(get_auth_repo)]
UserSupabaseRepoDep = Annotated[UserSupabaseRepo, Depends(get_user_supabase_repo)]