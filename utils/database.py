import sqlite3


def get_cursor() -> sqlite3.Cursor:
    return CONNECTION.cursor()


def init_database() -> None:
    global CONNECTION
    CONNECTION = sqlite3.connect("./data/database.db")


def close_database() -> None:
    CONNECTION.close()
