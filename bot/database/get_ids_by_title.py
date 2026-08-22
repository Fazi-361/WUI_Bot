import sqlite3
from jellyfish import jaro_winkler_similarity


class Game:
    """ Rappresenta un gioco con il suo titolo, ID e la somiglianza al titolo cercato.

    Attributes:
        title (str): Il titolo del gioco
        id (str): L'ID del gioco
        similarity (float): La somiglianza del titolo del gioco con il titolo cercato

    """

    def __init__(self, title: str, id: str, similarity: float) -> None:
        self.title = title
        self.id = id
        self.similarity = similarity

    def __repr__(self) -> str:
        return f"Game(title='{self.title}', id='{self.id}', similarity={self.similarity})"

    def pretty_print(self) -> str:
        return f"{self.title} - {self.id}"


def get_ids_by_title(title: str, region: str, similarity: float) -> list[Game]:
    """ Restituisce una lista di ID che migliori che combaciano al meglio al titolo dato in input.

    Args:
        title (str): Titolo del gioco del quale si vuole sapere l'ID
        region (str): Regione del gioco del quale si vuole sapere l'ID (NOTE: Può essere solo PAL, NTSC-U, NTSC-J)
        similarity (float): Limite di somiglianza sotto il quale non si vuole ricevere gli ID.

    Returns:
        list[Game]: Una lista di oggetti Game con i dati dei giochi trovati
    """

    # Regioni e il loro codice rispettivo
    regions = {
        "PAL": "P",
        "NTSC-U": "E",
        "NTSC-J": "J"
    }

    if region not in regions:
        raise ValueError(
            f"Regione '{region}' non valida. Regioni valide: {', '.join(regions)}"
        )

    region_id = regions[region]
    similarity = min(max(0, similarity), 1)
    games: list[Game] = []

    with sqlite3.connect("./data/database.db") as connection:
        cursor = connection.cursor()
        connection.create_function("JARO_WINKLER", 2, jaro_winkler_similarity)

        # Query per selezionare l'ID del gioco in base alla somiglianza al titolo
        # dato in input, usando l'algoritmo Jaro-Winkler. Uno stesso gioco compare
        # in GameLocale una volta per ogni lingua: con ROW_NUMBER() teniamo solo
        # la riga (lingua) con la similarità più alta per ciascun GameID.
        cursor.execute("""
            WITH scored AS (
                SELECT
                    gl.MiniID || gl.Region || COALESCE(gp.PublisherID, '') AS GameID,
                    gl.Title,
                    JARO_WINKLER(LOWER(gl.Title), ?) AS Similarity,
                    ROW_NUMBER() OVER (
                        PARTITION BY gl.MiniID || gl.Region || COALESCE(gp.PublisherID, '')
                        ORDER BY JARO_WINKLER(LOWER(gl.Title), ?) DESC
                    ) AS rn
                FROM GameLocale gl
                JOIN GamePublisher gp
                    ON gp.Console = gl.Console
                   AND gp.GameType = gl.GameType
                   AND gp.MiniID = gl.MiniID
                   AND gp.Region = gl.Region
                WHERE gp.Region = ?
            )
            SELECT GameID, Title, Similarity
            FROM scored
            WHERE rn = 1
              AND Similarity > ?
            ORDER BY Similarity DESC;
        """, (title.lower(), title.lower(), region_id, similarity))

        raw_results = cursor.fetchall()
        for game_id, game_title, sim in raw_results:
            games.append(Game(title=game_title, id=game_id, similarity=sim))

    return games


if __name__ == "__main__":
    try:
        games = get_ids_by_title(input("Inserire il gioco da cercare:\n"), "PAL", 0.95)
    except ValueError as e:
        print(f"Errore: {e}")
    else:
        if not games:
            print("Nessun gioco trovato con quel titolo/regione.")
        elif max(game.similarity for game in games) > 0.99:
            response = max(games, key=lambda game: game.similarity).id
            print(response)
        else:
            print(f"Possibili ID:\n{"\n".join([game.pretty_print() for game in games])}")