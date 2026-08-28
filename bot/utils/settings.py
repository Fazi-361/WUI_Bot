from enum import Enum
from typing import Any, TYPE_CHECKING, overload

from aiogram.fsm.context import FSMContext


class Settings(Enum):
    show_covers = True

    if TYPE_CHECKING:
        from types import CoroutineType

        @overload
        def __call__(self, state: FSMContext) -> CoroutineType[Any, Any, Any]: ...

        @overload
        def __call__(self, state: dict) -> Any: ...

    def __call__(self, state: FSMContext | dict):
        return (state.get_value if isinstance(state, FSMContext) else state.get)(
            self.name, self.value
        )
