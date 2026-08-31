from enum import Enum
from functools import lru_cache

from aiogram.filters import BaseFilter
from aiogram.types import Message
from regex_spm import fullmatch_in

from . import CCommand
from ..database.title_exists import gameid_exists, mastercode_exists
from ..utils.text import strim


class TextType(Enum):
    NONE = 0
    COMMAND = 1
    QUERY = 2
    GAME_ID = 3
    HASH = 4
    MASTER_CODE = 5
    
    def __call__(self, *data):
        self.data = data
        return self


@lru_cache(maxsize=10)
def text_type(text: str | None) -> TextType:
    if not text or len(text) < 2:
        return TextType.NONE
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
            return TextType.GAME_ID if gameid_exists(text) else TextType.QUERY
        #               CRC         MD5          SHA1
        case r"(?i)^(?:[0-9A-F]{8}|[0-9A-F]{32}|[0-9A-F]{40})$":
            return TextType.HASH
        #              System                                  ShortID
        case r"(?i)^.*(DOL|NTR|RVL|TWL|CTR|WUP|KTR)-(?:\w+-)*([0-9A-Z]{4}).*$" as m:
            return (
                TextType.MASTER_CODE(output[0], output[1], m[2])
                if (output := mastercode_exists(m[1], m[2]))
                else TextType.QUERY
            )

    return TextType.QUERY


class MessageType(BaseFilter):
    def __init__(self, *types: TextType) -> None:
        self.types: tuple[TextType, ...] = types

    async def __call__(self, message: Message) -> dict[str, TextType | None] | bool:
        return (
            {"message_type": t}
            if message.text is not None
            and (t := text_type(strim(message.text))) in self.types
            else False
        )
