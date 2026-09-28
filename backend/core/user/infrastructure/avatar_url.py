from urllib.parse import unquote, urlsplit

from core.user.domain.user_avatar import UserAvatar
from core.user.domain.user_error import InvalidUserAvatarError

_MARKER = "/object/public/avatars/"


def object_path(value: str) -> str:
    stripped = value.strip()
    if "://" not in stripped:
        return UserAvatar(stripped).value

    parts = urlsplit(stripped)
    if parts.scheme not in {"http", "https"}:
        raise InvalidUserAvatarError("El avatar debe ser una imagen del bucket propio")

    marker = parts.path.find(_MARKER)
    if marker == -1:
        raise InvalidUserAvatarError("El avatar debe ser una imagen del bucket propio")

    candidate = unquote(parts.path[marker + len(_MARKER) :])
    return UserAvatar(candidate).value


def public_avatar_url(supabase_url: str, path: str) -> str:
    base = supabase_url.rstrip("/")
    return f"{base}/storage/v1/object/public/avatars/{path}"
