import sqlite3

def get_random_title(console: str = "Wii") -> str:
    """ Restituisce il titolo di un gioco su gameTDB della console data in input.

    Args:
        console (str): Console del gioco. Wii per default

    Returns:
        str: Un titolo random
    """
    
    with sqlite3.connect("./data/database.db") as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT DISTINCT Title FROM BaseGameLocale
            WHERE Console = ?
            ORDER BY RANDOM()
            LIMIT 1;
        """, (console,))

        result = str(cursor.fetchone()[0])

    return result


if __name__ == "__main__":
    print(get_random_title())