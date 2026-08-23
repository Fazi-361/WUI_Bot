import sqlite3

def get_titles_by_ids(ids: list[str]) -> list[str]:
    """Data la lista di ID di giochi WII / GC, trova i nomi dei giochi corrispondenti.

    Args:
        ids (list[str]): Lista degli ID dei giochi da cercare

    Returns:
        list[str]: Lista dei nomi dei giochi corrispondenti agli ID dati in input
    """    

    game_names: list[str] = []

    with sqlite3.connect("./data/database.db") as connection:
        cursor = connection.cursor()
        for id in ids:
            id = id.strip()
            miniID = id[:3]
            region = id[3]
            publisherID = id[4:] if len(id) > 4 else None
            
            # Query per selezionare il titolo del gioco in base al MiniID, alla regione e al PublisherID
            game_name = cursor.execute(
                """            
                    SELECT gl.Title
                    FROM GameLocale gl
                    JOIN GamePublisher gp
                        ON gp.Console = gl.Console
                    AND gp.GameType = gl.GameType
                    AND gp.MiniID = gl.MiniID
                    AND gp.Region = gl.Region
                    WHERE gl.MiniID = ?
                    AND gl.Region = ?
                    AND (gp.PublisherID = ? OR (gp.PublisherID IS NULL AND ? IS NULL));
              """,
                (miniID, region, publisherID, publisherID)
            ).fetchone()
            
            game_names.append(f"{id} non trovato" if game_name is None else game_name[0])

    return game_names

if __name__ == "__main__":
    print(get_titles_by_ids(input("Inserire gli ID dei giochi da cercare separati da uno spazio:\n").upper().split()))