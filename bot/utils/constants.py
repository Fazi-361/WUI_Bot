from typing import TYPE_CHECKING

if TYPE_CHECKING:
    BOT_USERNAME: str
    BOT_CREATORS: list[str] | tuple[str, ...] | set[str]
    LANGS_REGION: dict[str, str]
    CONSOLE_CODE: dict[str, tuple[str, str]]
    COVERS_ATYPE: dict[str, tuple[str, str]]


def init_constants() -> None:
    global \
        BOT_USERNAME, \
        BOT_CREATORS, \
        LANGS_REGION, \
        CONSOLE_CODE, \
        COVERS_ATYPE

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
        #       Console  GameType
        "DOL": ("Wii" , "GameCube"), # 0 stored as Wii
        "NTR": ("DS"  , "DS"      ),
        "RVL": ("Wii" , "Wii"     ),
        "TWL": ("DS"  , "DSi"     ),
        "CTR": ("3DS" , "3DS"     ),
        "WUP": ("WiiU", "WUP"     ),
        "KTR": ("3DS" , "New3DS"  )
    }
    coverfullHQ = ('coverfullHQ', 'png')
    coverHQ = ('coverHQ', 'jpg')
    COVERS_ATYPE = {
        "Wii" : coverfullHQ,
        "DS"  : coverHQ    ,
        "WiiU": coverHQ    ,
        "3DS" : coverHQ    ,
    }
