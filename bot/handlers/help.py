from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n import I18n

from bot.filters import (
    CCommand,
    help_botcommand,
    info_botcommand,
    settings_botcommand,
    start_botcommand,
)

help_router: Router = Router()


@help_router.message(CCommand(help_botcommand))
async def help(message: Message, i18n: I18n) -> None:
    _ = i18n.gettext
    await message.reply(
        f"{_("help.header")}\n"
        f"/{start_botcommand.command} {_("command.start.description")}\n"
        f"/{help_botcommand.command} {_("command.help.description")}\n"
        f"/{settings_botcommand.command} {_("command.settings.description")}\n"
        f"/{info_botcommand.command} {_("command.info.description")}\n"
        # TODO: da rivedere questi in basso
        "/echo Ripete la parola data\n"
        "/deid Restituisce il gioco della Wii o Gamecube corrispondente all'ID dato.\n"
        "/id Restituisce l'ID di un gioco della Wii o Gamecube dato il nome.\n"
    )
