import re
from .database import CONNECTION
from unidecode import unidecode
from functools import lru_cache
from jellyfish import jaro_winkler_similarity


@lru_cache
def get_title_by_name(input: str, region: str = 'P') -> tuple[str, str, str] | None:
    input = re.sub(r'[^\w\s]', '', unidecode(input.upper()))
    input_split: list[str] = input.split()

    @lru_cache 
    def similarity(str1: str) -> float:
        str1 = re.sub(r'[^\w\s]', '', unidecode(str1))
        str1_split: list[str] = str1.split()
        str2_split: list[str] = input_split.copy()

        similarity: float = jaro_winkler_similarity(str1, input)
        for word1 in str1_split:
            for word2 in str2_split:
                if (word_similarity := jaro_winkler_similarity(word1, word2)) >= .8:
                    str2_split.remove(word2)
                    similarity += word_similarity
                    break

        return similarity

    CONNECTION.create_function("SIMILARITY", 1, similarity)
    cursor = CONNECTION.cursor()

    data = cursor.execute(
        """WITH Codes AS (
            WITH c AS (
                SELECT Console, GameType, MiniID, Region, PublisherID, SIMILARITY(UPPER(Title)) Similarity
                FROM BaseGameLocale
                WHERE Similarity >= ?
            )
            SELECT DISTINCT Console, GameType, MiniID, Region, PublisherID
            FROM c
            WHERE Similarity = (SELECT MAX(Similarity) FROM c)
        ), Regions AS (
            Select Region FROM Codes
        )
        SELECT Console, GameType, MiniID || Region || COALESCE(PublisherID, '')
        FROM Codes
        WHERE Region = ?
        OR NOT ? IN Regions AND Region = 'E'
        OR NOT 'E' IN Regions AND Region = 'P'
        OR NOT 'P' IN Regions AND Region = 'J'
        OR NOT 'J' IN Regions
        LIMIT 1""",
        [(input_len := len(input.split())) - input_len/10, region, region]
    ).fetchone()

    cursor.close()
    return data or None