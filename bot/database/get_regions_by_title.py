from functools import cache

from . import use_cursor
from ..utils import C

REGIONS_QUERY: str = f"""--sql
SELECT DISTINCT Lang, Region, Title, MiniID || Region || COALESCE(PublisherID, '')
FROM BaseGameLocale
WHERE Console = ? AND GameType = ? AND MiniID = ?
{
    '\n'.join(f"AND (Lang != '{lang}' OR Region IN {regions})"
    for lang, regions in C.PASS_REGIONS.items()
    if len(regions) > 1)
}
AND ((Lang != 'SE' AND Lang != 'FI') OR Region IN ('V', 'W'))
AND ((Lang != 'ZHCN' AND Lang != 'ZHTW') OR Region = 'W')
ORDER BY Region DESC
"""


@cache
def get_regions_by_title(
    title_console: str, title_type: str, title_mini_id: str
) -> list[tuple[str, str, str, str]]:
    """
    Ritorna: lingua, regione, nome e gameID
    """
    with use_cursor() as cursor:
        return cursor.execute(
            REGIONS_QUERY,
            [title_console, title_type, title_mini_id],
        ).fetchall()
