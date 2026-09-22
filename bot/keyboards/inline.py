from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..filters.callbacks import SettingsCallback

OPEN_SETTINGS: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🌐 Settings 🛠️",
                callback_data=SettingsCallback(option="open").pack(),
            )
        ]
    ]
)
