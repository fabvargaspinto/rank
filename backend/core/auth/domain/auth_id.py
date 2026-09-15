from dataclasses import dataclass


@dataclass(frozen=True)
class AuthId:
    value: str

