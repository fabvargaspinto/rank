from __future__ import annotations

import hmac
import json
from base64 import urlsafe_b64decode
from hashlib import sha256
from typing import Any


class InvalidSignedRequestError(ValueError):
    pass


def parse_signed_request(signed_request: str, app_secret: str) -> dict[str, Any]:
    try:
        encoded_sig, payload = signed_request.split(".", 1)
    except ValueError as exc:
        raise InvalidSignedRequestError("signed_request inválido") from exc

    expected = hmac.new(
        app_secret.encode("utf-8"),
        payload.encode("utf-8"),
        sha256,
    ).digest()
    received = urlsafe_b64decode(_pad(encoded_sig))
    if not hmac.compare_digest(received, expected):
        raise InvalidSignedRequestError("Firma de signed_request inválida")

    try:
        data = json.loads(urlsafe_b64decode(_pad(payload)))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidSignedRequestError("Payload de signed_request inválido") from exc

    if not isinstance(data, dict):
        raise InvalidSignedRequestError("Payload de signed_request inválido")
    return data


def _pad(value: str) -> bytes:
    padded = value + ("=" * (-len(value) % 4))
    return padded.encode("ascii")
