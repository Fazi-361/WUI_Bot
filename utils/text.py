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
class TextType(Enum):
    QUERY = 1
    GAME_ID = 2


@lru_cache()
def text_type(text: str) -> TextType | None:
    if len(text) < 3:
        return None

    match fullmatch_in(text):
        #            System               Title      Region                   Publisher
        case r"(?i)^[0-9CDEFGHJLMNPQRSWX][0-9A-Z]{2}[ABDEFHIJKLMNPQRSTUVWXYZ](?:[0-9A-Z]{2})?$":
            return TextType.GAME_ID

    return TextType.QUERY