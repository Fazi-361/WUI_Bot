from functools import cache

from . import use_cursor
from ..filters import TextType as T, text_type


@cache
def get_title_by_hash(checksum: str) -> tuple[str, str, str] | None:
    if text_type(checksum) is not T.HASH:
        return None

    with use_cursor() as cursor:
        return cursor.execute(
            f"""SELECT Console, GameType, MiniID || Region || COALESCE(PublisherID, '')
            FROM BaseGameROM
            WHERE { {8: 'CRC', 32: 'MD5', 40: 'SHA1'}[len(checksum)] } = ?
            LIMIT 1
            """,
            [checksum]
        ).fetchone()
