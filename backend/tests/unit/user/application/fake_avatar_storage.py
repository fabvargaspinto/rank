class FakeAvatarStorage:
    def __init__(self) -> None:
        self.uploads: list[tuple[str, bytes, str]] = []
        self.deleted: list[str] = []
        self.url = "https://example.supabase.co/storage/v1/object/public/avatars/user/avatar.jpg"

    def upload(self, auth_id: str, content: bytes, content_type: str) -> str:
        self.uploads.append((auth_id, content, content_type))
        return self.url

    def delete(self, auth_id: str) -> None:
        self.deleted.append(auth_id)
