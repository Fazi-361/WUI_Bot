import re

# Regex che corrisponde all'ID di un gioco
ID_PATTERN = re.compile(
    r"^[0-9CDEFGHJLMNPQRSWX][0-9A-Z]{2}[ABDEFHIJKLMNPQRSTUVWXYZ](?:[0-9A-Z]{2})?$",
    re.IGNORECASE,
)


def is_game_id(text: str) -> bool:
    """
    Verifica se la stringa data è l'ID di un gioco.

    Esempi:
        is_game_id("ST7P01")           -> True 
        is_game_id("st7p")             -> True 
        is_game_id("not-an-id")        -> False
    """
    if not text:
        return False

    candidate = text.strip().upper()

    if len(candidate) not in {4, 6}:
        return False

    if not ID_PATTERN.fullmatch(candidate):
        return False

    return True