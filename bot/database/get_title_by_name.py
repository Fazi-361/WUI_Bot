from functools import lru_cache, partial

from jellyfish import jaccard_similarity as ja, jaro_winkler_similarity as jw
from unidecode import unidecode_expect_nonascii as unidecode

from . import CONNECTION, use_cursor
from ..utils import C
from ..utils.text import strim

CONNECTION.create_function("JW", 2, partial(jw, long_tolerance=True))


@lru_cache
def get_title_by_name(input: str, lang: str) -> tuple[str, str, str] | None:
    input = unidecode(strim(input.upper()), errors="preserve")
    input_split: list[str] = input.split()

    def similarity(str1: str) -> float:
        if input == (str1 := unidecode(str1, errors="preserve")):
            return 100

        similarity: float = ja(str1, input)
        str1_split: list[str] = str1.split()
        highest_index: int = 0
        for word2 in input_split:
            for i, word1 in enumerate(str1_split[highest_index:], 1):
                if (word_similarity := jw(word2, word1)) >= 0.8:
                    highest_index += i
                    similarity += word_similarity
                    break

        return similarity

    CONNECTION.create_function("SIMILARITY", 1, similarity)
    with use_cursor() as cursor:
        pass_regions: tuple[str, ...] = C.PASS_REGIONS.get(lang) or ()
        return cursor.execute(
            f"""WITH Codes AS (
                SELECT DISTINCT Console, GameType, MiniID, Region, PublisherID
                FROM BaseGameLocale
                WHERE JW(Title, (
                    SELECT Title
                    FROM (
                        SELECT Title, SIMILARITY(UPPER(Title)) Similarity
                        FROM DistinctTitles
                        WHERE Similarity >= :treshold
                        ORDER BY Similarity DESC
                        LIMIT 1
                    ) _
                )) >= 0.98
            ), Regions AS (
                Select DISTINCT Region FROM Codes
            )
            SELECT Console, GameType, MiniID || Region || COALESCE(PublisherID, '')
            FROM Codes
            WHERE Region = :usual
            {
                f'OR :usual NOT IN Regions AND Region IN {pass_regions}\n'
                f'OR {' AND '.join(f"{region!r} NOT IN Regions" for region in pass_regions)}'
                if pass_regions else ''
            }
            LIMIT 1""",
            {
                "treshold": len(input_split) * 0.9 + 0.2,
                "usual": C.USUAL_REGION.get(lang),
            },
        ).fetchone()
