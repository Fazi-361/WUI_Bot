from typing import TYPE_CHECKING
if TYPE_CHECKING:
    BOT_USERNAME: str

def init_constants() -> None:
    global BOT_USERNAME
    
    BOT_USERNAME = "" # filled in later by bot.py on start