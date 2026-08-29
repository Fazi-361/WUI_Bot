from functools import lru_cache
import re

from jellyfish import jaro_winkler_similarity
from unidecode import unidecode

from . import CONNECTION, use_cursor


@lru_cache
def get_title_by_name(input: str, region: str = "P") -> tuple[str, str, str] | None:
    input = re.sub(r"[^\w\s]", "", unidecode(input.upper()))
    input_split: list[str] = input.split()
    input_split_len: int = len(input_split)

    def similarity(str1: str) -> float:
        str1 = re.sub(r"[^\w\s]", "", unidecode(str1))
        str2_split: list[str] = input_split.copy()

        similarity: float = jaro_winkler_similarity(str1, input, True)
        if similarity == 1:
            return input_split_len * 100

        for word1 in str1.split():
            for word2 in str2_split:
                if (word_similarity := jaro_winkler_similarity(word1, word2)) >= 0.8:
                    str2_split.remove(word2)
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
            [input_split_len - input_split_len / 10, region, region],
        ).fetchone()
