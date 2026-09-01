from json import dumps, loads
from sqlite3 import connect
from typing import Any, Mapping, override

from aiogram.filters.state import StateType
from aiogram.fsm.state import State
from aiogram.fsm.storage.base import BaseStorage, StorageKey


class SQLiteStorage(BaseStorage):
    def __init__(self) -> None:
        self.conn = connect("./data/userdata.db")
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS FSM (
                Key TEXT PRIMARY KEY,
                State TEXT,
                Data TEXT
            )"""
        )
        self.conn.commit()

    def resolve_state(self, value: StateType) -> str | None:
        if value is None:
            return None
        if isinstance(value, State):
            return value.state
        return str(value)

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        self.conn.execute(
            """INSERT INTO FSM (Key, State) VALUES (:key, :state)
            ON CONFLICT DO UPDATE SET State = :state""",
            {"key": str(key), "state": self.resolve_state(state)}
        )
        self.conn.commit()

    async def get_state(self, key: StorageKey) -> str | None:
        return data[0] if (data := self.conn.execute(
            "SELECT State FROM FSM WHERE Key = ? LIMIT 1",
            [str(key)]
        ).fetchone()) else None

    async def set_data(self, key: StorageKey, data: Mapping[str, Any]) -> None:
        self.conn.execute(
            """INSERT INTO FSM (Key, Data) VALUES (:key, :data)
            ON CONFLICT DO UPDATE SET Data = :data""",
            {"key": str(key), "data": dumps(data)}
        )
        self.conn.commit()

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        return loads(data) if (data := self.conn.execute(
            "SELECT Data FROM FSM WHERE Key = ? LIMIT 1",
            [str(key)]
        ).fetchone()) and (data := data[0]) else {}

    @override
    async def get_value(
        self,
        storage_key: StorageKey,
        dict_key: str,
        default: Any | None = None,
    ) -> Any | None:
        return loads(data) if (data := self.conn.execute(
            "SELECT Data -> ? FROM FSM WHERE Key = ? LIMIT 1",
            [dict_key, str(storage_key)]
        ).fetchone()) and (data := data[0]) else default

    @override
    async def update_data(self, key: StorageKey, data: Mapping[str, Any]) -> dict[str, Any]:
        current_data = loads(self.conn.execute(
            """INSERT INTO FSM (Key, Data) VALUES (:key, :data)
            ON CONFLICT DO UPDATE SET Data = json_patch(Data, :data)
            RETURNING Data""",
            {"key": str(key), "data": dumps(data)}
        ).fetchone()[0])
        self.conn.commit()
        return current_data
    
    async def delete(self, key: StorageKey) -> None:
        self.conn.execute("DELETE FROM FSM WHERE KEY = ?", [str(key)])
        self.conn.commit()

    async def close(self) -> None:
        self.conn.commit()
        self.conn.close()
