from functools import cache

from . import use_cursor


@cache
def get_regions_by_title(
    title_console: str, title_type: str, title_mini_id: str
) -> list[tuple[str, str, str, str]]:
    """
    Ritorna: lingua, regione, nome e gameID
    """
    with use_cursor() as cursor:
        return cursor.execute(
            """SELECT DISTINCT Lang, Region, Title, MiniID || Region || COALESCE(PublisherID, '')
            FROM BaseGameLocale
            WHERE Console = ? AND GameType = ? AND MiniID = ?
            AND (Lang != 'JA' OR Region IN ('A', 'J'))
            AND (Lang != 'US' OR Region IN ('A', 'E', 'N', 'X', 'Y', 'Z'))
            AND (Lang != 'EN' OR Region IN ('A', 'P', 'H', 'U', 'X', 'Y', 'Z', 'J'))
            AND (Lang != 'DE' OR Region IN ('A', 'D', 'P', 'L', 'M', 'H', 'U', 'X', 'Y', 'Z'))
            AND (Lang != 'FR' OR Region IN ('A', 'F', 'P', 'L', 'M', 'H', 'U', 'X', 'Y', 'Z'))
            AND (Lang != 'IT' OR Region IN ('A', 'I', 'P', 'L', 'M', 'H', 'U', 'X', 'Y', 'Z'))
            AND (Lang != 'ES' OR Region IN ('A', 'S', 'P', 'L', 'M', 'H', 'U', 'X', 'Y', 'Z'))
            AND (Lang != 'KO' OR Region IN ('A', 'K', 'Q', 'T'))
            AND ((Lang != 'SE' AND Lang != 'FI') OR Region IN ('V', 'W'))
            AND ((Lang != 'ZHCN' AND Lang != 'ZHTW') OR Region = 'W')
            ORDER BY Region DESC""",
            [title_console, title_type, title_mini_id],
        ).fetchall()
