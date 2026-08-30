from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n import I18n
from aiogram.filters import CommandObject

from bot.filters import CCommand, hashes_botcommand
from bot.database.get_hashes import *

hashes_router: Router = Router()


@hashes_router.message(CCommand(hashes_botcommand))
def hashes(message: Message, command: CommandObject, i18n: I18n):
    """Dato l'ID o il titolo del gioco, restituisce i suoi hash"""
    
    game = command.args
    result = pretty_print(get_hashes(game))

    return message.reply(result)
