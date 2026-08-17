from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n import I18n

from bot.filters.command import CustomCommand

help_router: Router = Router()


@help_router.message(CustomCommand("help"))
async def help(message: Message, i18n: I18n) -> None:
    _ = i18n.gettext
    await message.reply(
        f"{_("help.header")}\n"
        f"/start {_("command.start.description")}\n"
        f"/help {_("command.help.description")}\n"
        f"/settings {_("command.settings.description")}\n"
        f"/info {_("command.info.description")}\n"
        "/echo Ripete la parola data\n"
        "/deid Restituisce il gioco della Wii o Gamecube corrispondente all'ID dato.\n"
        "/id Restituisce l'ID di un gioco della Wii o Gamecube dato il nome.\n"
    )
