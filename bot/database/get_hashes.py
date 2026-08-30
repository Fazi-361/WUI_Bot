import sqlite3
from .get_ids_by_title import get_ids_by_title
from ..utils.is_game_id import is_game_id

def get_hashes(game: str) -> dict[str, str]:
    """ Restituisce le hash dei giochi che corrispondono al titolo dato.

    Params:
        game (str): ID del gioco di cui si vuole sapere gli hash

    Returns:
        dict[str, str]: Una hash (haha, get it?) map che contiene il CRC, MD5 e SHA del gioco
    """

    # dizionario da restituire
    hashes: dict[str, str] = {
        "CRC"  : "",
        "MD5"  : "",
        "SHA1" : ""
    }

    # Trasforma il gioco nel suo corrispondente id nel caso abbiamo ricevuto un titolo
    if not is_game_id(game):
        try:
            game = get_ids_by_title(game, "PAL", 0.95)[0].id
        except IndexError:
            return None

    game = game.strip().upper()
    miniID = game[:3]
    region = game[3]
    publisherID = game[4:] if len(game) > 4 else None
    
    with sqlite3.connect("./data/database.db") as connection:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT CRC, MD5, SHA1
            FROM BaseGameROM
            WHERE
                MiniID       = ? AND
                Region       = ? AND
                PublisherID  = ? ;
        """, (miniID, region, publisherID))

        hashes["CRC"], hashes["MD5"], hashes["SHA1"] = cursor.fetchone()

    return hashes

def pretty_print(hashes: dict[str, str]):
    string = ""
    for key in hashes:
        string += f"{key}  :  {hashes[key]}\n"

    return string.strip()

if __name__ == "__main__":
    try:
        result = get_hashes(input("Inserire il gioco da cercare:\n"))
    except:
        print(f"Errore")
    else:
        if not result:
            print("Nessun gioco trovato.")
        else:
            print(pretty_print(result))