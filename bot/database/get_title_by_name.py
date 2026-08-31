from functools import lru_cache

from jellyfish import jaro_winkler_similarity as jws
from unidecode import unidecode_expect_nonascii as unidecode

from . import CONNECTION, use_cursor
from ..utils.text import strim


@lru_cache
def get_title_by_name(input: str, region: str = "P") -> tuple[str, str, str] | None:
    input = unidecode(strim(input.upper()), errors="preserve")
    input_split: list[str] = input.split()
    treshold: float = 0.82

    def similarity(str1: str) -> float:
        if input == (str1 := unidecode(str1, errors="preserve")):
            return 100

        str1_split: list[str] = str1.split()
        similarity: float = jws(input, str1, True)

        highest_index: int = 0
        for word2 in input_split:
            for i, word1 in enumerate(str1_split[highest_index:], 1):
                if (word_similarity := jws(word2, word1)) >= treshold:
                    highest_index += i
                    similarity += word_similarity
                    break

        return similarity

    CONNECTION.create_function("SIMILARITY", 1, similarity)
    with use_cursor() as cursor:
        return cursor.execute(
            """WITH Codes AS (
                SELECT DISTINCT Console, GameType, MiniID, Region, PublisherID
                FROM BaseGameLocale
                WHERE Title = (
                    SELECT Title
                    FROM (
                        SELECT Title, SIMILARITY(UPPER(Title)) Similarity
                        FROM DistinctTitles
                        WHERE Similarity >= ?
                        ORDER BY Similarity DESC
                    ) _
                    LIMIT 1
                )
            ), Regions AS (
                Select DISTINCT Region FROM Codes
            )
            SELECT Console, GameType, MiniID || Region || COALESCE(PublisherID, '')
            FROM Codes
            WHERE Region = ?
            OR NOT ? IN Regions AND Region = 'E'
            OR NOT 'E' IN Regions AND Region = 'P'
            OR NOT 'P' IN Regions AND Region = 'J'
            OR NOT 'J' IN Regions
            LIMIT 1""",
            [(1 - treshold) + len(input_split) * 0.9, region, region],
        ).fetchone()
