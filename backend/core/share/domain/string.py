from core.share.domain.domain_error import InvalidStringError 

class String:
    value: str

    def __init__(self, value: str):
        self.value = self.validate(value)

    @classmethod
    def validate(cls, value: str) -> str:
        if not value or not str(value).strip():
            raise InvalidStringError("String is required")
        return value

    def __str__(self) -> str:
        return self.value