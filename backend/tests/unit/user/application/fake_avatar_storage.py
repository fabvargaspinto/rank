class FakeAvatarStorage:
    def __init__(self) -> None:
        self.uploads: list[tuple[str, bytes, str]] = []
        self.deleted: list[str] = []

    def upload(self, path: str, content: bytes, content_type: str) -> None:
        self.uploads.append((path, content, content_type))

    def delete(self, path: str) -> None:
        self.deleted.append(path)
