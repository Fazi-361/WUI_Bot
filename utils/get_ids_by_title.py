import sqlite3
from jellyfish import jaro_winkler_similarity

def get_ids_by_title(title: str, region: str, similarity: float) -> list[str]:
    """ Restituisce una lista di ID che migliori che combaciano al meglio al titolo dato in input.

    Args:
        title (str): Titolo del gioco del quale si vuole sapere l'ID
        region (str): Regione del gioco del quale si vuole sapere l'ID (NOTE: Può essere solo PAL, NTSC-U, NTSC-J)
        similarity (float): Limite di somiglianza sotto il quale non si vuole ricevere gli ID.

    Returns:
        list[str]: Una lista degli ID migliori
    """    """"""

    # Regioni e il loro codice rispettivo
    regions = {
        "PAL": "P",
        "NTSC-U": "E",
        "NTSC-J": "J"
    }
    
    if region not in regions:
        print(f"Errore: la regione '{region}' non è valida.\nRegioni valide: {[key for key in regions.keys()]}")
        return []
    
    region_id = regions[region]
    ids: list[str] = []
    

    with sqlite3.connect("./data/database.db") as connection:
        similarity = min(max(0, similarity), 1)
        cursor = connection.cursor()
        connection.create_function("JARO_WRINKLER", 2, jaro_winkler_similarity)

        # Query per selezionare il MiniID e il PublisherID in base alla simiglianza al titolo dato in input usando l'algoritmo Jaro Wrinkler
        cursor.execute("""
            SELECT DISTINCT MiniID, PublisherID
            FROM GameLocalePublisher
            WHERE Region = ? AND JARO_WRINKLER(LOWER(Title), ?) > ?
            ORDER BY JARO_WRINKLER(LOWER(Title), ?) DESC
        """, (region_id, title.lower(), similarity, title.lower()))

        raw_ids = cursor.fetchall()
        for raw_id in raw_ids:
            # Unisco MiniID, codice della regione e PublisherID in una sola stringa per ottenere il codice corretto.
            ids.append(f"{raw_id[0]}{region_id}{raw_id[1] if raw_id[1] is not None else ""}")

    return ids

if __name__ == "__main__":
    print(get_ids_by_title(input("Inserire il gioco da cercare:\n"), "PAL", 0.9))