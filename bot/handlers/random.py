from random import randint

from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n import I18n
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext

from bot.filters import CCommand, random_botcommand
from bot.database.get_random_title import get_random_title
from .info import info

random_router: Router = Router()

@random_router.message(CCommand(random_botcommand))
async def random(message: Message, command: CommandObject, state: FSMContext, i18n: I18n):
    _ = i18n.gettext

    console: str | None = command.args

    valid_consoles: list[str] = [
        "Wii",
        "DS",
        "3DS",
        "WiiU"
    ]

    if console is None:
        console = valid_consoles[randint(0, len(valid_consoles)-1)]

    for valid_console in valid_consoles:
        if console.lower() == valid_console.lower():
            console = valid_console

    if console not in valid_consoles:
        await message.reply(_("random.invalid_console"))

    else:
        random_title = get_random_title(console)
        # print(random_title)
        await info(message, state, random_title, i18n)
