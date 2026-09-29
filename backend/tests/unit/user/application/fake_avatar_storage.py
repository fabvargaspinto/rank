class FakeAvatarStorage:
    def __init__(self) -> None:
        self.uploads: list[tuple[str, bytes, str]] = []
        self.deleted: list[str] = []

    def upload(self, path: str, content: bytes, content_type: str) -> None:
        self.uploads.append((path, content, content_type))

    def delete(self, auth_id: str) -> None:
        self.deleted.append(auth_id)
