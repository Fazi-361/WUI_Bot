import sqlite3


def get_id_by_title(
    input: str,
    region: str = 'P'
) -> str:
    cursor = get_cursor()
    data = cursor.execute(
        """WITH Codes AS (
            SELECT DISTINCT 
                MiniID, Region, PublisherID
            FROM GameLocalePublisher
            WHERE UPPER(Title) = UPPER(?)
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
        [input, region, region]
    ).fetchone()
    
    if not data or not (data := data[0]):
        ... # TODO: case if no result

    return data


def get_cursor() -> sqlite3.Cursor:
    return CONNECTION.cursor()


def init_database() -> None:
    global CONNECTION
    CONNECTION = sqlite3.connect("./data/database.db")


def close_database() -> None:
    CONNECTION.close()
    

if __name__ == "__main__":
    init_database()
    print(get_id_by_title('itadaki street wii'))