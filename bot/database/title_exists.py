from functools import cache

from . import use_cursor
from ..utils import C


@cache
def mastercode_exists(console_code: str, short_id: str) -> tuple[str, str] | bool:
    if len(console_code) != 3 or len(short_id) != 4 \
    or not (console_and_type := C.CONSOLE_CODE.get(console_code)):
        return False

    short_id = short_id.upper()
    with use_cursor() as cursor:
        return console_and_type if cursor.execute(
            """SELECT 1
            FROM GamePublisher
            WHERE Console = ?
            AND GameType = ?
            AND MiniID = ?
            AND Region = ?
            """,
            [console_and_type[0], console_and_type[1], short_id[:3], short_id[3]]
        ).fetchone() else False


@cache
def gameid_exists(title_id: str) -> bool:
    """
    Controlla se un titolo Wii esiste nel database dall'ID
    """

    if len(title_id) not in {4, 6}:
        return False

    title_id = title_id.upper()
    publisher: str = title_id[4:6]

    with use_cursor() as cursor:
        return bool(cursor.execute(
            f"""SELECT 1
            FROM GamePublisher
            WHERE Console = 'Wii'
            AND MiniID = ?
            AND Region = ?
            {"AND PublisherID = ?" if publisher else ''}
            """,
            [title_id[:3], title_id[3]]
            + ([publisher] if publisher else [])
        ).fetchone())
