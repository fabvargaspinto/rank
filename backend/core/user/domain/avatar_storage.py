from typing import Protocol


class AvatarStorage(Protocol):
    def upload(
        self,
        path: str,
        content: bytes,
        content_type: str,
    ) -> None:
        pass

    def delete(self, path: str) -> None:
        pass
