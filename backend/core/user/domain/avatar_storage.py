from typing import Protocol


class AvatarStorage(Protocol):
    def upload(
        self,
        auth_id: str,
        content: bytes,
        content_type: str,
    ) -> str:
        pass
