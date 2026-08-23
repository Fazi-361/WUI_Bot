from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n import I18n
from aiogram.filters import CommandObject

from bot.filters import CCommand, deid_botcommand
from bot.database.get_titles_by_ids import get_titles_by_ids

deid_router: Router = Router()

@deid_router.message(CCommand(deid_botcommand))
async def deid(message: Message, command: CommandObject) -> None:
    """Data la lista di ID di giochi WII / GC, trova i nomi dei giochi corrispondenti."""
    
    if not command.args:
        await message.reply("Scrivere l'ID dei giochi da cercare dopo lo /. \nesempio: /deid R8PE01 ST7P01")
        return

    game_names: list[str] = get_titles_by_ids(command.args.upper().split())

    response = "\n".join(game_names)
    await message.reply(response)
