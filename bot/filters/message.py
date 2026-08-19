from enum import Enum
from functools import lru_cache

from aiogram.filters import BaseFilter
from aiogram.types import Message
from regex_spm import fullmatch_in

from . import CCommand
from ..database import title_exists
from ..utils.text import strim 


class TextType(Enum):
    COMMAND = 1
    QUERY = 2
    GAME_ID = 3
    HASH = 4


@lru_cache()
def text_type(text: str | None) -> TextType | None:
    if not text or len(text) < 2:
        return None
    elif text[0] in CCommand.prefix:
        return TextType.COMMAND

    match fullmatch_in(text):
        case (
            # System
            r"(?i)^[0-9CDEFGHJLMNPQRSWX]"
            # Title
            r"[0-9A-Z]{2}"
            # Region
            r"[ABDEFHIJKLMNPQRSTUVWXYZ]"
            # Publisher
            r"(?:[0-9A-Z]{2})?$"
        ):
            return TextType.GAME_ID if title_exists(text) else TextType.QUERY
        #               crc         md5          sha1
        case r"(?i)^(?:[0-9A-F]{8}|[0-9A-F]{32}|[0-9A-F]{40})$":
            return TextType.HASH

    return TextType.QUERY


class MessageType(BaseFilter):
    def __init__(self, *types: TextType | None) -> None:
        self.types: tuple[TextType | None, ...] = types

    async def __call__(self, message: Message) -> bool:
        return message.text is not None and text_type(strim(message.text)) in self.types
