import re

from domain.Share.string import String
from domain.error.domain_error import InvalidURLError

URL_REGEX = re.compile(r"^https?://[^\s/$.?#].[^\s]*$")
MAX_URL_LENGTH = 2048
MIN_URL_LENGTH = 10


class URL(String):
    @classmethod
    def validate(cls, value: str) -> str:
        url = value.strip()

        if len(url) < MIN_URL_LENGTH:
            raise InvalidURLError("URL is too short")
        if len(url) > MAX_URL_LENGTH:
            raise InvalidURLError("URL is too long")
        if not URL_REGEX.match(url):
            raise InvalidURLError("URL is not valid")

        return url
