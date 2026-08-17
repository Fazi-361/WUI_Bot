import sqlite3

CONNECTION: sqlite3.Connection = sqlite3.connect("./data/database.db")


def get_cursor() -> sqlite3.Cursor:
    return CONNECTION.cursor()


def close_database() -> None:
    CONNECTION.close()


__all__ = [
    "get_cursor",
    "close_database",
    "CONNECTION"
]