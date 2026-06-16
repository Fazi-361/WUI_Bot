import sqlite3
from jellyfish import jaro_winkler_similarity

def get_ids_by_title(title: str, region: str, similarity: float) -> list:
    regions = {
        "PAL": "P",
        "NTSC-U": "E",
        "NTSC-J": "J"
    }
    
    if region not in regions:
        print(f"Errore: la regione '{region}' non è valida.\nRegioni valide: {[key for key in regions.keys()]}")
        return []
    
    region_id = regions[region]
    ids: list = []
    
    title_lower = title.lower()

    with sqlite3.connect("./data/database.db") as connection:
        similarity = min(max(0, similarity), 1)
        cursor = connection.cursor()
        connection.create_function("JARO_WRINKLER", 2, jaro_winkler_similarity)

        cursor.execute("""
            SELECT DISTINCT MiniID, PublisherID
            FROM GameLocalePublisher
            WHERE Region = ? AND JARO_WRINKLER(LOWER(Title), ?) > ?
            ORDER BY JARO_WRINKLER(LOWER(Title), ?) DESC
        """, (region_id, title_lower, similarity, title_lower))

        raw_ids = cursor.fetchall()
        for raw_id in raw_ids:
            ids.append(f"{raw_id[0]}{region_id}{raw_id[1] if raw_id[1] is not None else ""}")

    return ids

if __name__ == "__main__":
    print(get_ids_by_title(input("Inserire il gioco da cercare:\n"), "PAL", 0.9))