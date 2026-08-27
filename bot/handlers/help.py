from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n import I18n

from bot.filters.commands import CCommand, help_botcommand, BOTCOMMANDS

help_router: Router = Router()


@help_router.message(CCommand(help_botcommand))
def help(message: Message, i18n: I18n):
    _ = i18n.gettext
    return message.reply(
        f"{_("help.header")}\n{'\n'.join(
            f'/{command.command}: {_(command.description)}'
            for command in BOTCOMMANDS
        )}"
    )
