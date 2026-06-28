from typing import TYPE_CHECKING
if TYPE_CHECKING:
    BOT_USERNAME: str
    LANG_REGIONS: dict[str, str]
    DEFAULT_ANSWER_LANG: str

def init_constants() -> None:
    global BOT_USERNAME, \
           LANG_REGIONS, \
           DEFAULT_ANSWER_LANG
    
    BOT_USERNAME = "" # filled in later by bot.py on start
    LANG_REGIONS = {
        "US": "E",
        "EN": "P",
        "DE": "P",
        "FR": "P",
        "ES": "P",
        "IT": "P",
        "JA": "J",
        "KO": "K"
    }
    DEFAULT_ANSWER_LANG = "EN"
