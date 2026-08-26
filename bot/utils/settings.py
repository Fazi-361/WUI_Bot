from enum import Enum
from typing import Any


class Settings(Enum):
    show_covers = True
    
    @property
    def key(self) -> tuple[str, Any]:
        return (self.name, self.value)
