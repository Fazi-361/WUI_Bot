from contextlib import contextmanager
import sqlite3

CONNECTION: sqlite3.Connection = sqlite3.connect("./data/database.db")


@contextmanager
def use_cursor():
    connection = get_cursor()
    try:
        yield connection
    finally:
        connection.close()


def get_cursor() -> sqlite3.Cursor:
    return CONNECTION.cursor()


def close_database() -> None:
    CONNECTION.close()


from .get_regions_by_title import get_regions_by_title
from .get_title_by_hash import get_title_by_hash
from .get_title_by_name import get_title_by_name
from .get_title_page import get_title_page
from .title_exists import title_exists

__all__ = (
    "get_regions_by_title",
    "get_title_by_hash",
    "get_title_by_name",
    "get_title_page",
    "title_exists",
    "use_cursor",
    "get_cursor",
    "close_database",
    "CONNECTION"
)