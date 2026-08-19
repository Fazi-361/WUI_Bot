import sqlite3

CONNECTION: sqlite3.Connection = sqlite3.connect("./data/database.db")


def get_cursor() -> sqlite3.Cursor:
    return CONNECTION.cursor()


def close_database() -> None:
    CONNECTION.close()


from .get_title_by_hash import get_title_by_hash
from .get_title_by_name import get_title_by_name
from .get_title_page import get_title_page
from .title_exists import title_exists

__all__ = [
    "get_title_by_hash",
    "get_title_by_name",
    "get_title_page",
    "title_exists",
    "get_cursor",
    "close_database",
    "CONNECTION"
]