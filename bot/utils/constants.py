from typing import TYPE_CHECKING

if TYPE_CHECKING:
    BOT_USERNAME: str
    BOT_CREATORS: list[str] | tuple[str, ...] | set[str]
    LANGS_REGION: dict[str, str]
    CONSOLE_CODE: dict[str, str]


def init_constants() -> None:
    global \
        BOT_USERNAME, \
        BOT_CREATORS, \
        LANGS_REGION, \
        CONSOLE_CODE

    BOT_USERNAME = "" # filled in later by bot.py on start
    BOT_CREATORS = [] # filled in later by bot.py on start
    LANGS_REGION = {
        "US": "E",
        "EN": "P",
        "DE": "P",
        "FR": "P",
        "ES": "P",
        "IT": "P",
        "JA": "J",
        "KO": "K"
    }
    CONSOLE_CODE = {
        "DOL": "Wii", # Stored as Wii
        "NTR": "DS",
        "RVL": "Wii",
        "TWL": "DS",
        "CTR": "3DS",
        "WUP": "WiiU",
        "KTR": "3DS"
    }
