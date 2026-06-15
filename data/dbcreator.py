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
            MiniID TEXT NOT NULL,
            Type TEXT DEFAULT `Wii`,
            Developer TEXT,
            
            PRIMARY KEY (MiniID, Type)
        ) STRICT;

        CREATE TABLE IF NOT EXISTS GamePublisher (
            MiniID TEXT NOT NULL,
            Type TEXT DEFAULT `Wii`,
            Region TEXT NOT NULL,
            PublisherID TEXT,
            Publisher TEXT,

            UNIQUE (MiniID, Type, Region, PublisherID, Publisher),
            FOREIGN KEY (MiniID, Type)
                REFERENCES Game(MiniID, Type)
                ON DELETE CASCADE,
            FOREIGN KEY (PublisherID)
                REFERENCES Company(Code)
                ON DELETE CASCADE,
            CHECK(
                (PublisherID ISNULL AND Publisher NOTNULL)
                OR
                (PublisherID NOTNULL AND Publisher ISNULL)
            )
        ) STRICT;

        CREATE TABLE IF NOT EXISTS GameLocale (
            Lang TEXT NOT NULL,
            Title TEXT NOT NULL,
            Synopsis TEXT,
            MiniID TEXT NOT NULL,
            Type TEXT DEFAULT `Wii`,
            Region TEXT NOT NULL,
            
            PRIMARY KEY (Lang, MiniID, Type, Region),
            FOREIGN KEY (MiniID, Type)
                REFERENCES Game(MiniID, Type)
                ON DELETE CASCADE
        ) STRICT;
        
        CREATE TABLE IF NOT EXISTS GameRelease (
            MiniID TEXT NOT NULL,
            Type TEXT DEFAULT `Wii`,
            Region TEXT NOT NULL,
            Date TEXT NOT NULL,
            
            UNIQUE (MiniID, Type, Region),
            FOREIGN KEY (MiniID, Type)
                REFERENCES Game(MiniID, Type)
                ON DELETE CASCADE
        ) STRICT;
        
        CREATE TABLE IF NOT EXISTS GameROM (
            MiniID TEXT NOT NULL,
            Type TEXT DEFAULT `Wii`,
            Region TEXT NOT NULL,
            Version TEXT NOT NULL,
            CRC TEXT,
            MD5 TEXT,
            SHA1 TEXT,
            
            UNIQUE (MiniID, Type, Region, Version, CRC, MD5, SHA1),
            FOREIGN KEY (MiniID, Type)
                REFERENCES Game(MiniID, Type)
                ON DELETE CASCADE
        ) STRICT;"""
    )
    
    for game in games:
        # Removes custom games and homebrews
        if (game_type := game.find("type")) is not None and bool(game_type := game_type.text) and game_type.casefold() in {"custom", "homebrew"}:
            continue
        
        # Filter out games that don't meet certain criteria. For each game, log who it is
        if ((game_id := game.find("id")) is None or (game_id := game_id.text) is None or len(game_id) not in {4, 6}) \
        or ((game_date := game.find("date")) is None or not {"year", "month", "day"}.issubset(game_date.attrib)) \
        or len(game_locales := game.findall("locale")) < 1 \
        or len(game_roms := game.findall("rom")) < 1:
            print(f"{game.attrib["name"]} has been skipped.")
            continue

        if not game_type: game_type = "Wii"
        game_id = game_id.upper()
        game_mini_id: str | None      = game_id[:3] or None
        game_region: str              = game_id[3]
        game_publisher_id: str | None = game_id[4:] or None
        game_year: str  = game_date.attrib["year"].rjust(4, '0')
        game_month: str = game_date.attrib["month"].rjust(2, '0')
        game_day: str   = game_date.attrib["day"].rjust(2, '0')

        CURSOR.execute(
            "INSERT OR IGNORE INTO Game VALUES (?, ?, ?)",
            [
                game_mini_id,
                game_type,
                game_developer.text
                    if (game_developer := game.find("developer")) is not None
                    else None
            ]
        )
        
        game_publisher = None
        if game_publisher_id \
        or ((game_publisher := game.find("publisher")) is not None
        and (game_publisher := game_publisher.text)):
            CURSOR.execute(
                "INSERT OR REPLACE INTO GamePublisher VALUES (?, ?, ?, ?, ?)",
                [
                    game_mini_id,
                    game_type,
                    game_region,
                    game_publisher_id or None,
                    game_publisher
                ]
            )

        for game_locale in game_locales:
            if (game_title := game_locale.find("title")) is None:
                continue
            
            game_synopsis = game_synopsis.text \
                if (game_synopsis := game_locale.find("synopsis")) is not None \
                else None
            
            CURSOR.execute(
                "INSERT OR REPLACE INTO GameLocale VALUES (?, ?, ?, ?, ?, ?)",
                [
                    game_locale.attrib["lang"].upper(),
                    game_title.text,
                    game_synopsis,
                    game_mini_id,
                    game_type,
                    game_region,
                ]
            )
        
        CURSOR.execute(
            "INSERT OR REPLACE INTO GameRelease VALUES (?, ?, ?, ?)",
            [
                game_mini_id,
                game_type,
                game_region,
                "-".join([game_year, game_month, game_day])
            ]
        )
        
        for game_rom in game_roms:
            if not (game_rom_version := game_rom.attrib["version"]):
                continue

            CURSOR.execute(
                "INSERT OR IGNORE INTO GameROM VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    game_mini_id,
                    game_type,
                    game_region,
                    game_rom_version,
                    game_rom.attrib.get("crc"),
                    game_rom.attrib.get("md5"),
                    game_rom.attrib.get("sha1")
                ]
            )
    
    print("Games have been inserted")
        

print("Saving...")
CONNECTION.commit()
print("Changes saved to database.\nClosing...")
CURSOR.close()
CONNECTION.close()