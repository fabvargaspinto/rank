import hmac
import json
from base64 import urlsafe_b64encode
from hashlib import sha256

import pytest

from core.instagram.infrastructure.signed_request import (
    InvalidSignedRequestError,
    parse_signed_request,
)

APP_SECRET = "app-secret"


def _signed_request(payload: dict, secret: str = APP_SECRET) -> str:
    body = urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("ascii").rstrip("=")
    signature = urlsafe_b64encode(
        hmac.new(secret.encode("utf-8"), body.encode("utf-8"), sha256).digest()
    ).decode("ascii").rstrip("=")
    return f"{signature}.{body}"


def test_parse_signed_request_round_trip():
    payload = {"user_id": "17841400000000000", "algorithm": "HMAC-SHA256"}

    assert parse_signed_request(_signed_request(payload), APP_SECRET) == payload


def test_parse_signed_request_rejects_bad_signature():
    token = _signed_request({"user_id": "1"}, secret="other")

    with pytest.raises(InvalidSignedRequestError):
        parse_signed_request(token, APP_SECRET)
