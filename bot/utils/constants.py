from typing import TYPE_CHECKING

if TYPE_CHECKING:
    BOT_USERNAME: str
    BOT_CREATORS: list[str] | tuple[str, ...] | set[str]
    USUAL_REGION: dict[str, str]
    PASS_REGIONS: dict[str, tuple[str, ...]]
    CONSOLE_CODE: dict[str, tuple[str, str]]
    COVER_SOURCE: dict[str, tuple[str, str]]


def init_constants() -> None:
    global \
        BOT_USERNAME, \
        BOT_CREATORS, \
        USUAL_REGION, \
        PASS_REGIONS, \
        CONSOLE_CODE, \
        COVER_SOURCE

    BOT_USERNAME = "" # filled in later by bot.py on start
    BOT_CREATORS = [] # filled in later by bot.py on start
    USUAL_REGION = {
        "US": "E",
        "EN": "P",
        "DE": "P",
        "FR": "P",
        "ES": "P",
        "IT": "P",
        "JA": "J",
        "KO": "K"
    }
    PASS_REGIONS = {
        'JA'  : ('A', 'J'),
        'US'  : ('A', 'E', 'N', 'X', 'Y', 'Z'),
        'EN'  : ('A', 'P', 'H', 'U', 'V', 'X', 'Y', 'Z', 'J'),
        'DE'  : ('A', 'D', 'P', 'L', 'M', 'H', 'U', 'V', 'X', 'Y', 'Z'),
        'FR'  : ('A', 'F', 'P', 'L', 'M', 'H', 'U', 'V', 'X', 'Y', 'Z'),
        'IT'  : ('A', 'I', 'P', 'L', 'M', 'H', 'U', 'V', 'X', 'Y', 'Z'),
        'ES'  : ('A', 'S', 'P', 'L', 'M', 'H', 'U', 'V', 'X', 'Y', 'Z'),
        'NL'  : ('A', 'H', 'P', 'L', 'M', 'U', 'V', 'X', 'Y', 'Z'),
        'KO'  : ('A', 'K', 'Q', 'T'),
        'ZHCN': ('W',),
        'ZHTW': ('W',)
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
    COVER_SOURCE = {
        "Wii" : coverfullHQ,
        "DS"  : coverHQ    ,
        "WiiU": coverHQ    ,
        "3DS" : coverHQ    ,
    }
