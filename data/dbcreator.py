if __name__ != "__main__":
    exit()


import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

PATH: Path                     = Path(__file__).parent.resolve()
CONNECTION: sqlite3.Connection = sqlite3.connect(PATH/"database.db")
CURSOR: sqlite3.Cursor         = CONNECTION.cursor()


CURSOR.execute("PRAGMA foreign_keys = OFF")
"""
For some reason there's a bug where enabling foreign_keys makes
some inserts not work. There's absolutely no error printed out
to the console, it just doesn't insert them. That's weird.
"""

def gen(tree, root, console) -> None:
    CURSOR.execute(
        """CREATE TABLE IF NOT EXISTS Company (
            Console TEXT NOT NULL,
            CompanyName TEXT NOT NULL,
            CompanyCode TEXT NOT NULL,
            
            PRIMARY KEY (Console, CompanyName, CompanyCode)
        ) STRICT, WITHOUT ROWID"""
    )

    if (companies := root.find('companies')) is None:
        print(f"{console}: Companies do not exist")
    else:
        CURSOR.executemany(
            "INSERT OR REPLACE INTO Company VALUES (?, ?, ?)",
            [
                (console,  company.attrib["name"], company.attrib["code"].upper())
                for company in companies.iter('company')
            ] + [(console, 'Nintendo', "00"), (console, '?', '-')]
        )

        print(f"{console}: Companies have been inserted")

    CURSOR.executescript(
        """CREATE TABLE IF NOT EXISTS Game (
            Console TEXT NOT NULL,
            GameType TEXT NOT NULL,
            MiniID TEXT NOT NULL,
            Developer TEXT,

            PRIMARY KEY (Console, GameType, MiniID)
        ) STRICT;
        
        CREATE TABLE IF NOT EXISTS GamePublisher (
            Console TEXT NOT NULL,
            GameType TEXT NOT NULL,
            MiniID TEXT NOT NULL,
            Region TEXT NOT NULL,
            PublisherID TEXT,
            PublisherName TEXT,
            PublishDate TEXT NOT NULL,

            FOREIGN KEY (Console, GameType, MiniID)
                REFERENCES Game(Console, GameType, MiniID)
                ON DELETE CASCADE,
            PRIMARY KEY (Console, GameType, MiniID, Region),
            CHECK (NOT (PublisherID NOTNULL AND PublisherName NOTNULL))
        ) STRICT;
        
        CREATE VIEW IF NOT EXISTS BaseGame AS
        SELECT *
        FROM Game NATURAL JOIN GamePublisher;
        
        CREATE TABLE IF NOT EXISTS GameLocale (
            Console TEXT NOT NULL,
            GameType TEXT NOT NULL,
            MiniID TEXT NOT NULL,
            Region TEXT NOT NULL,
            Lang TEXT NOT NULL,
            Title TEXT NOT NULL,
            Synopsis TEXT,
            
            FOREIGN KEY (Console, GameType, MiniID, Region)
                REFERENCES GamePublisher(Console, GameType, MiniID, Region)
                ON DELETE CASCADE,
            PRIMARY KEY (Console, GameType, MiniID, Region, Lang)
        ) STRICT;
        
        CREATE VIEW IF NOT EXISTS BaseGameLocale AS
        SELECT *
        FROM BaseGame NATURAL JOIN GameLocale;
        
        CREATE TABLE IF NOT EXISTS GameROM (
            Console TEXT NOT NULL,
            GameType TEXT NOT NULL,
            MiniID TEXT NOT NULL,
            Region TEXT NOT NULL,
            ROMVersion TEXT NOT NULL,
            CRC TEXT,
            MD5 TEXT,
            SHA1 TEXT,
            
            FOREIGN KEY (Console, GameType, MiniID, Region)
                REFERENCES GamePublisher(Console, GameType, MiniID, Region)
                ON DELETE CASCADE,
            PRIMARY KEY (Console, GameType, MiniID, Region, ROMVersion)
        ) STRICT;
        """
    )

    if (games := root.iter('game')) is None:
        print(f"{console}: Games do not exist")
    else:
        for game in games:
            game_type: str | None = None
            
            # Removes custom games and homebrews
            if (_ := game.find("type")) is not None \
            and (game_type := _.text) \
            and game_type.casefold() in {"custom", "homebrew"}:
                continue
            
            # Filter out games that don't meet certain criteria. For each game, log who it is
            if ((_ := game.find("id")) is None 
                or (game_id := _.text) is None 
                or len(game_id) not in {4, 6}) \
            or ((game_date := game.find("date")) is None
                or not {"year", "month", "day"}.issubset(game_date.attrib)) \
            or len(locales := game.findall("locale")) < 1 \
            or len(roms := game.findall("rom")) < 1:
                print(f"{game.attrib["name"]} has been skipped.")
                continue

            game_id: str = game_id.upper()
            game_mini_id: str      = game_id[:3]
            game_region: str       = game_id[3]
            game_publisher_id: str = game_id[4:]
            game_developer: str | None = (_.text or None) \
                if (_ := game.find("developer")) is not None \
                else None

            # insert missing developers with no code
            # CURSOR.execute(
            #     """INSERT INTO Company
            #     SELECT ?, ?, '-'
            #     WHERE NOT EXISTS (
            #         SELECT 1
            #         FROM Company
            #         WHERE Console = ?
            #         AND Developer = ?
            #     )""",
            #     [
            #         console,
            #         game_company_name
            #     ] * 2
            # )

            CURSOR.execute(
                "INSERT OR REPLACE INTO Game VALUES (?, ?, ?, ?)",
                [
                    console,
                    game_type or console,
                    game_mini_id,
                    game_developer # or None
                ]
            )
            
            game_publisher_name: str | None = (_.text or None) \
                if (_ := game.find("publisher")) is not None \
                else None
            game_publish_date: str = (
                f"{game_date.attrib["year"].rjust(4, '0')}-"
                f"{game_date.attrib["month"].rjust(2, '0')}-"
                f"{game_date.attrib["day"].rjust(2, '0')}"
            )

            CURSOR.execute(
                "INSERT OR REPLACE INTO GamePublisher VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    console,
                    game_type or console,
                    game_mini_id,
                    game_region,
                    game_publisher_id or None,
                    None if game_publisher_id else game_publisher_name, # or None
                    game_publish_date
                ]
            )

            for locale in locales:
                if (_ := locale.find("title")) is None \
                or not (game_title := _.text):
                    continue
                
                game_synopsis: str | None = (_.text or None) \
                    if (_ := locale.find("synopsis")) is not None \
                    else None
                
                game_lang: str = locale.attrib["lang"].upper()
                if game_lang == "EN" and game_region == "E":
                    game_lang = "US"

                CURSOR.execute(
                    "INSERT OR REPLACE INTO GameLocale VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [
                        console,
                        game_type or console,
                        game_mini_id,
                        game_region,
                        game_lang,
                        game_title,
                        game_synopsis # or None
                    ]
                )
            
            for rom in roms:
                if not (game_rom_version := rom.attrib["version"]):
                    continue

                CURSOR.execute(
                    "INSERT OR REPLACE INTO GameROM VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        console,
                        game_type or console,
                        game_mini_id,
                        game_region,
                        game_rom_version,
                        rom.attrib.get("crc"), # or None
                        rom.attrib.get("md5"), # or None
                        rom.attrib.get("sha1") # or None
                    ]
                )
        
        print(f"{console}: Games have been inserted")


for db, console in (
    ("wiitdb.xml", "Wii"),
    ("dstdb.xml", "DS"),
    ("wiiutdb.xml", "WiiU"),
    ("3dstdb.xml", "3DS"),
):
    with open(PATH/db, "r") as f:
        tree = ET.parse(f)
        root = tree.getroot()
        gen(tree, root, console)


print("Saving...")
CONNECTION.commit()
print("Changes saved to database.\nClosing...")
CURSOR.close()
CONNECTION.close()