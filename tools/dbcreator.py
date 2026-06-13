if __name__ != "__main__":
    exit()


import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

PATH: Path                     = Path(__file__).parent.resolve()
CONNECTION: sqlite3.Connection = sqlite3.connect(PATH/"database.db")
CURSOR: sqlite3.Cursor         = CONNECTION.cursor()


CURSOR.execute("PRAGMA foreign_keys = ON")

with open(PATH/"wiitdb.xml", "r") as f:
    tree = ET.parse(f)
    root = tree.getroot()


if (companies := root.find('companies')) is None:
    print("Companies do not exist")
else:
    CURSOR.execute(
        """CREATE TABLE IF NOT EXISTS Company (
            Code TEXT PRIMARY KEY,
            Name TEXT NOT NULL
        ) STRICT, WITHOUT ROWID"""
    )
    
    CURSOR.executemany(
        "INSERT OR REPLACE INTO Company VALUES (?, ?)",
        [
            (company.attrib["code"].upper(), company.attrib["name"])
            for company in companies.iter('company')
        ] + [('00', "Nintendo")]
    )

    print("Companies have been inserted")
    

if (games := root.iter('game')) is None:
    print("Games do not exist")
else:
    CURSOR.executescript(
        """CREATE TABLE IF NOT EXISTS Game (
            ShortID TEXT PRIMARY KEY,
            PublisherID TEXT NOT NULL,
            
            UNIQUE (ShortID, PublisherID),
            FOREIGN KEY (PublisherID)
                REFERENCES Company(Code)
                ON DELETE CASCADE
        ) STRICT, WITHOUT ROWID;
        
        CREATE TABLE IF NOT EXISTS GameLocale (
            Lang TEXT NOT NULL,
            Title TEXT NOT NULL,
            Synopsis TEXT,
            Game TEXT NOT NULL,
            
            PRIMARY KEY (Lang, Title),
            FOREIGN KEY (Game)
                REFERENCES Game(ShortID)
                ON DELETE CASCADE
        ) STRICT;
        
        CREATE TABLE IF NOT EXISTS GameRelease (
            ID TEXT PRIMARY KEY,
            ShortID TEXT UNIQUE NOT NULL,
            Date TEXT NOT NULL,
            
            FOREIGN KEY (ShortID)
                REFERENCES Game(ShortID)
                ON DELETE CASCADE
        );"""
    )
    
    for game in games:
        # Removes custom games and games which are missing some keys
        if (game_type := game.find("type")) is None \
        or game_type.text == "CUSTOM" \
        or (game_id := game.find("id")) is None \
        or (game_id := game_id.text) is None \
        or len(game_id) != 6 \
        or (game_date := game.find("date")) is None \
        or not {"year", "month", "day"}.issubset(game_date.attrib) \
        or len(game_locales := game.findall("locale")) < 1:
            continue

        game_id = game_id.upper()
        game_short_id: str = game_id[:3]
        game_year: str = game_date.attrib["year"].rjust(4, '0')
        game_month: str = game_date.attrib["month"].rjust(2, '0')
        game_day: str = game_date.attrib["day"].rjust(2, '0')

        try: 
            CURSOR.execute(
                "INSERT OR IGNORE INTO Game VALUES (?, ?)",
                [
                    game_short_id,
                    game_id[4:]
                ]
            )
        except:
            print(game_id)
            exit()

        for game_locale in game_locales:
            if (game_title := game_locale.find("title")) is None:
                continue
            
            game_synopsis = game_synopsis.text \
                if (game_synopsis := game_locale.find("synopsis")) is not None \
                else None
            
            CURSOR.execute(
                "INSERT OR REPLACE INTO GameLocale VALUES (?, ?, ?, ?)",
                [
                    game_locale.attrib["lang"].upper(),
                    game_title.text,
                    game_synopsis,
                    game_short_id
                ]
            )
        
        CURSOR.execute(
            "INSERT OR REPLACE INTO GameRelease VALUES (?, ?, ?)",
            [
                game_id,
                game_short_id,
                "-".join([game_year, game_month, game_day])
            ]
        )
    
    print("Games have been inserted")
        

print("Saving...")
CONNECTION.commit()
print("Changes saved to database.\nClosing...")
CURSOR.close()
CONNECTION.close()