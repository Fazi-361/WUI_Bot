from aiogram import Router
from aiogram.types import Message
from aiogram.utils.i18n import I18n
from aiogram.filters import CommandObject

from bot.filters import CCommand, id_botcommand
from bot.database.get_ids_by_title import get_ids_by_title

id_router: Router = Router()

@id_router.message(CCommand(id_botcommand))
async def id(message: Message, command: CommandObject) -> None:
    """Dato il nome di un gioco, restituisce l'ID del gioco corrispondente"""
    #TODO: Dare la possibilità di cercare la regione del gioco (pal, ntsc-u, ntsc-j). Per ora il predefinito è PAL. 
    #TODO 2 electric boogaloo: gestire le lingue

    if not command.args:
        await message.reply("Inserire il del gioco dopo lo /. \nEsempio: /id Super Smash. Bros Brawl")
        return

    title = command.args

    games = get_ids_by_title(title, "PAL", 0.95)
    
    if games == []:
        response = "Non è stato trovato nessun gioco con questo nome"
    elif max(game.similarity for game in games) > 0.99:
        response = max(games, key=lambda game: game.similarity).id
    else:
        response = f"ID Possibili:\n{"\n".join([game.pretty_print() for game in games])}"

    await message.reply(response)
    