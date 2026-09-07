

class AuthId():
    def __init__(self, value: str):
        if not value:
            raise ValueError("Auth id cannot be empty")
        if value.isdigit():
            self.value = int(value)
        else:
            self.value = value
