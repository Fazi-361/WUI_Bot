"""
File lasciato per i comandi di Tayx da rivedere
"""


from aiogram.types import Message
from aiogram.filters import CommandObject


async def echo(message: Message, command: CommandObject) -> None:
    """Ripete la frase data come argomento."""

    await message.reply(
        command.args
        if command.args
        else "Scrivi qualcosa dopo /echo! Es: /echo ciao a tutti"
    )


async def deid(message: Message, command: CommandObject) -> None:
    """Data la lista di ID di giochi WII / GC, trova i nomi dei giochi corrispondenti."""
    
    if not command.args:
        await message.reply("Scrivere l'ID dei giochi da cercare dopo lo /. \nesempio: /deid R8PE01 ST7P01")
        return

    from .database.get_titles_by_ids import get_titles_by_ids

    game_names: list[str] = get_titles_by_ids(command.args.split())

    response = "\n".join(game_names)
    await message.reply(response)


async def id(message: Message, command: CommandObject) -> None:
    """Dato il nome di un gioco, restituisce l'ID del gioco corrispondente"""
    #TODO: Dare la possibilità di cercare la regione del gioco (pal, ntsc-u, ntsc-j). Per ora il predefinito è PAL. 

    if not command.args:
        await message.reply("Inserire il del gioco dopo lo /. \nEsempio: /id Super Smash. Bros Brawl")
        return

    title = command.args

    from .database.get_ids_by_title import get_ids_by_title

    games = get_ids_by_title(title, "PAL", 0.9)
    
    if games == []:
        response = "Non è stato trovato nessun gioco con questo nome"
    elif max(game.similarity for game in games) > 0.99:
        response = max(games, key=lambda game: game.similarity).id
    else:
        possible_games = "\n".join(f"{game.title} - {game.id}" for game in games)
        response = f"ID possibili:\n{possible_games}"

    await message.reply(response)


async def copertina_id(message: Message, command: CommandObject) -> None:
    if not command.args:
        await message.reply("Inserisci un ID!")
        return

    args = command.args.split()
    lang_codes=["EN", "JA", "FR", "DE", "ES", "IT", "NL", "PT", "RU", "KO", "ZHCN", "ZHTW"]
    id = args[0]
    lang_code = "EN"  if id[3] != 'J' else "JA"
    if len(args) > 1: 
        lang_code = args[1].upper()
        if lang_code not in lang_codes:
            await message.reply("Codice della lingua non valido.")
            return

    try:
        await message.reply_photo(f"https://art.gametdb.com/wii/coverfullHQ/{lang_code}/{id}.png")
    except:
        await message.reply("Apparentemente non esiste una copertina di questo gioco su GameTDB nella lingua specificata..")


