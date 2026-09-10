from core.shared.domain.domain_error import InvalidStringError

from dataclasses import dataclass

@dataclass
class String:
    value: str
    
    def __post_init__(self):
        self.validate()
        
    def validate(self):
        if not isinstance(self.value, str):
            raise InvalidStringError("Invalid string")
        self.value = self.value.strip()
        