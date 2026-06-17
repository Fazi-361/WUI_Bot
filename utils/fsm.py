import sqlite3
from ast import literal_eval as eval
from typing import Any, Mapping
from aiogram.filters.state import StateType
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import BaseStorage, StorageKey

class BotState(StatesGroup):
    language = State()

class SQLiteStorage(BaseStorage):
    def __init__(self) -> None:
        self.conn = sqlite3.connect("./data/.userdb.db")
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS FSM (
                Key TEXT PRIMARY KEY,
                State TEXT,
                Data TEXT
            )"""
        )

    def resolve_state(self, value: StateType) -> str | None:
        if value is None:
            return None
        if isinstance(value, State):
            return value.state
        return str(value)

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        str_state = self.resolve_state(state)
        self.conn.execute(
            """INSERT INTO FSM (Key, State) VALUES (?, ?)
            ON CONFLICT DO UPDATE SET State = ?""",
            [str(key), str_state, str_state]
        )
        self.conn.commit()

    async def get_state(self, key: StorageKey) -> str | None:
        return data[0] if (data := self.conn.execute(
            "SELECT State FROM FSM WHERE Key = ?",
            [str(key)]
        ).fetchone()) else None

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
        str_data = str(data)
        self.conn.execute(
            """INSERT INTO FSM (Key, Data) VALUES (?, ?)
            ON CONFLICT DO UPDATE SET Data = ?""",
            [str(key), str_data, str_data]
        )
        self.conn.commit()

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        return eval(data) if (data := self.conn.execute(
            "SELECT Data FROM FSM WHERE Key = ?",
            [str(key)]
        ).fetchone()) and (data := data[0]) else {}

    async def close(self) -> None:
        self.conn.close()