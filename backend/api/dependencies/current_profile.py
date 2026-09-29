from typing import Annotated

from fastapi import Depends

from api.dependencies.auth import CurrentUser, get_current_user
from config.dependency_container import get_user_use_case
from core.user.application.get_user import GetUser
from core.user.domain.user import User


def get_current_profile(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    get_user: GetUser = Depends(get_user_use_case),
) -> User:
    return get_user.execute(current_user.auth_id)
