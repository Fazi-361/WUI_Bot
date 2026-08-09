from .text import text_type, TextTypes as T
from .database import get_cursor
from functools import lru_cache


@lru_cache()
def get_title_by_hash(checksum: str) -> tuple[str, str, str] | None:
    if text_type(checksum) is not T.HASH:
        return None

    cursor = get_cursor()
    data = cursor.execute(
        f"""SELECT Console, GameType, MiniID || Region || COALESCE(PublisherID, '')
        FROM BaseGameROM
        WHERE { {8: 'CRC', 32: 'MD5', 40: 'SHA1'}[len(checksum)] } = ?
        LIMIT 1
        """,
        [checksum]
    ).fetchone()

    cursor.close()
    return data or None