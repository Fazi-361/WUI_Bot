from functools import lru_cache
import re


@lru_cache()
def strim(text: str) -> str:
    return re.sub(
        pattern= r"\s+", 
        repl= ' ',
        string= text.strip()
    )


from regex_spm import fullmatch_in
from enum import Enum
class TextTypes(Enum):
    QUERY = 1
    GAME_ID = 2
    HASH = 3


@lru_cache()
def text_type(text: str) -> TextTypes | None:
    if len(text) < 3:
        return None

    match fullmatch_in(text):
        #            System               Title      Region                   Publisher
        case r"(?i)^[0-9CDEFGHJLMNPQRSWX][0-9A-Z]{2}[ABDEFHIJKLMNPQRSTUVWXYZ](?:[0-9A-Z]{2})?$":
            return TextTypes.GAME_ID
        #               crc         md5          sha1
        case r"(?i)^(?:[0-9A-F]{8}|[0-9A-F]{32}|[0-9A-F]{40})$":
            return TextTypes.HASH

    return TextTypes.QUERY