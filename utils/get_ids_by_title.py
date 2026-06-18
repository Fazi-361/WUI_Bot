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
        return [Game(
            title=f"Errore: la regione '{region}' non è valida.\nRegioni valide: PAL, NTSC-U, NTSC-J", 
            id="", 
            similarity=0)]
    
    region_id = regions[region]
    games: list[Game] = []
    
    with sqlite3.connect("./data/database.db") as connection:
        similarity = min(max(0, similarity), 1)
        cursor = connection.cursor()
        connection.create_function("JARO_WRINKLER", 2, jaro_winkler_similarity)

        # Query per selezionare il MiniID e il PublisherID in base alla simiglianza al titolo dato in input usando l'algoritmo Jaro Wrinkler
        cursor.execute("""
            SELECT DISTINCT 
                Title, MiniID, PublisherID, JARO_WRINKLER(LOWER(Title), ?) as Similarity
            FROM GameLocalePublisher
            WHERE Region = ? AND JARO_WRINKLER(LOWER(Title), ?) > ?
            ORDER BY JARO_WRINKLER(LOWER(Title), ?) DESC
        """, (title.lower(), region_id, title.lower(), similarity, title.lower()))

        raw_results = cursor.fetchall()
        for raw_result in raw_results:
            game_title, mini_id, publisher_id, sim = raw_result
            games.append(Game(title=game_title, 
                              id=f"{mini_id}{region_id}{publisher_id if publisher_id is not None else ''}", 
                              similarity=sim))

    return games

if __name__ == "__main__":
    games = get_ids_by_title(input("Inserire il gioco da cercare:\n"), "PAL", 0.9)

    if max(game.similarity for game in games) > 0.99:
        #print("here")
        response = max(games, key=lambda game: game.similarity).id
    else:
        possible_ids = [game.id for game in games]
        response = f"ID trovati:\n{possible_ids}"
    
    print(response)