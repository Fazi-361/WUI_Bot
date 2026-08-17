from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


LANGUAGE_OPTIONS: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🇺🇸 US", callback_data='US'),
        InlineKeyboardButton(text="🇬🇧 EN", callback_data='EN'),
        InlineKeyboardButton(text="🇩🇪 DE", callback_data='DE'),
        InlineKeyboardButton(text="🇫🇷 FR", callback_data='FR'),
    ],
    [
        InlineKeyboardButton(text="🇪🇸 ES", callback_data='ES'),
        InlineKeyboardButton(text="🇮🇹 IT", callback_data='IT'),
        InlineKeyboardButton(text="🇯🇵 JA", callback_data='JA'),
        InlineKeyboardButton(text="🇰🇷 KO", callback_data='KO'),
    ],
])