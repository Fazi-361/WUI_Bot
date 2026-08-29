from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n import I18n

from bot.filters import CCommand, start_botcommand

start_router: Router = Router()


@start_router.message(CCommand(start_botcommand))
def start(message: Message, i18n: I18n):
    return message.reply(f"{i18n.gettext("start.hello")}\n\n🇺🇸 To change language, use /settings")
