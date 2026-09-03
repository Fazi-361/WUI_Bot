from . import use_cursor


def get_random_title(console: str = "Wii") -> str:
    """ Restituisce il titolo di un gioco su gameTDB della console data in input.

    Args:
        console (str): Console del gioco. Wii per default

    Returns:
        str: Un titolo random
    """

    with use_cursor() as cursor:
        cursor.execute(
            """SELECT DISTINCT Title
            FROM BaseGameLocale
            WHERE Console = ?
            ORDER BY RANDOM()
            LIMIT 1""",
            [console]
        )

        return str(cursor.fetchone()[0])


if __name__ == "__main__":
    print(get_random_title())