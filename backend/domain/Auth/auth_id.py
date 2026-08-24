from domain.Share.uuid import UUID

class AuthId(UUID):
    def __init__(self, value: str):
        super().__init__(value)

    def __str__(self) -> str:
        return self.value