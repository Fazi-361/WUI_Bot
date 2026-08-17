from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n import I18n

from bot.filters.command import CustomCommand

start_router: Router = Router()


@start_router.message(CustomCommand("start"))
async def start(message: Message, i18n: I18n) -> None:
    await message.reply(f"{i18n.gettext("start.hello")}\n\n🇺🇸 To change language, use /settings")
    