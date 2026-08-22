from aiogram.fsm.state import State, StatesGroup


class BotState(StatesGroup):
    language = State()
