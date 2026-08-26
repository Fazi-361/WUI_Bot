from aiogram.filters.callback_data import CallbackData


class SettingsCallback(CallbackData, prefix="set"):
    option: str
