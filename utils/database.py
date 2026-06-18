import sqlite3


def get_id_by_title(
    input: str,
    region: str = 'P'
) -> str | list[tuple[str, str]]:
    cursor = get_cursor()
    
    data = cursor.execute(
        """WITH Codes AS (
            SELECT DISTINCT 
                MiniID, Region, PublisherID, SIMILARITY(UPPER(Title), UPPER(?)) Similarity
            FROM GameLocalePublisher
            WHERE Similarity >= ?
            ORDER BY Similarity DESC
        ), Regions AS (
            Select Region FROM Codes
        )
        SELECT MiniID || Region || COALESCE(PublisherID, '')
        FROM Codes
        WHERE Region = ?
        OR NOT ? IN Regions AND Region = 'E'
        OR NOT 'E' IN Regions AND Region = 'P'
        OR NOT 'P' IN Regions AND Region = 'J'
        OR NOT 'J' IN Regions
        LIMIT 1""",
        [input, len(input.split()) - .5, region, region]
    ).fetchone()
    
    if data and (data := data[0]):
        cursor.close()
        return data

    # data = cursor.execute(
    #     """SELECT Title, Key, SIMILARITY(UPPER(Title), UPPER(?)) c
    #     FROM (
    #         SELECT DISTINCT Title, MiniID || '-' || Type Key
    #         FROM GameLocalePublisher
    #     )
    #     ORDER BY c DESC
    #     LIMIT 3""",
    #     [input]
    # ).fetchall()
    
    # print(data)
    
    cursor.close()
    return data


def get_cursor() -> sqlite3.Cursor:
    return CONNECTION.cursor()


def init_database() -> None:
    global CONNECTION
    CONNECTION = sqlite3.connect("./data/database.db")
    
    
    from jellyfish import jaro_winkler_similarity
    from functools import lru_cache
    
    @lru_cache 
    def similarity(str1: str, str2: str) -> float:
        str1_split: list[str] = str1.split()
        str2_split: list[str] = str2.split()
        return sum([
            word_similarity
            if (word_similarity := jaro_winkler_similarity(word1, word2)) >= .8
            else 0
            for word2 in str2_split
            for word1 in str1_split
        ])

    CONNECTION.create_function("SIMILARITY", 2, similarity)


def close_database() -> None:
    CONNECTION.close()
    

if __name__ == "__main__":
    init_database()
    print(get_id_by_title('itadaki street wii'))