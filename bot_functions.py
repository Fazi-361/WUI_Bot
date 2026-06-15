import sqlite3

from aiogram.types import Message
from aiogram.filters import CommandObject
from jellyfish import jaro_winkler_similarity


async def start(message: Message) -> None:
    """Avvia il bot"""
    await message.reply('Bot ancora in beta! Ritorna più tardi :)')


async def help(message: Message) -> None:
    """Mostra la lista dei comandi"""

    await message.reply("""Ecco una lista dei comandi:
    /start - Avvia il bot
    /help - Mostra questo menù
    /echo - Ripete la parola data
    /deid - Restituisce il gioco della Wii o Gamecube corrispondente all'ID dato.
    /id   - Restituisce l'ID di un gioco della Wii o Gamecube dato il nome.""")


async def echo(message: Message, command: CommandObject) -> None:
    """Ripete la frase data come argomento."""

    await message.reply(
        " ".join(command.args)
        if command.args
        else "Scrivi qualcosa dopo /echo! Es: /echo ciao a tutti"
    )

async def deid(message: Message, command: CommandObject) -> None:
    """Data la lista di ID di giochi WII / GC, trova i nomi dei giochi corrispondenti."""
    
    if not command.args:
        await message.reply("Scrivere l'ID dei giochi da cercare dopo lo /. \nesempio: /deid R8PE01 ST7P01")
        return

    game_names: list[str] = []

    with sqlite3.connect("./tools/database.db") as connection:
        cursor = connection.cursor()
        for arg in command.args:
            id = arg.upper().strip()
            game_name = cursor.execute(
                """SELECT gl.Title
                FROM GameLocale gl
                JOIN GamePublisher gp
                ON gl.MiniID = gp.MiniID
                AND gl.Type = gp.Type
                WHERE (gl.MiniID || gl.Region || COALESCE(gp.PublisherID, '')) = ?
                LIMIT 1""",
                [id]
            ).fetchone()
            
            game_names.append(f"{id} non orato" if game_name is None else game_name[0])

    response = "\n".join(game_names)
    await message.reply(response)


async def id(message: Message, command: CommandObject) -> None:
    """Dato il nome di un gioco, restituisce l'ID del gioco corrispondente"""

    if not command.args:
        await message.reply("Scrivere il nome del gioco da cercare dopo lo /. \nEsempio: /id La via della fortuna")
        return

    game_name = " ".join(command.args).strip().lower()

    best_similarity: float = 0
    best_id: str = ""    
    with open("wiitdb.txt", "r", encoding="utf-8") as database:
        for line in database:
            is_wiiware = True if line[5] == "=" else False
            line_game_name = line[7:].lower().strip() if is_wiiware else line[9:].lower().strip()
            similarity = jaro_winkler_similarity(game_name, line_game_name)
            if similarity > best_similarity:
                best_similarity = similarity
                best_id = line[:4] if is_wiiware else line[:6]
    response: str = ""
    if best_similarity > 0.8:
        response = best_id
    else:
        response = "Gioco non trovato"
        
    await message.reply(response)

async def copertina_id(message: Message, command: CommandObject) -> None:
    if not command.args:
        await message.reply("Inserisci un ID!")
        return

    lang_codes=["EN", "JA", "FR", "DE", "ES", "IT", "NL", "PT", "RU", "KO", "ZHCN", "ZHTW"]
    id = command.args[0]
    lang_code = "EN"  if id[3] != 'J' else "JA"
    if len(command.args) > 1: 
        lang_code = command.args[1].upper()
        if lang_code not in lang_codes:
            await message.reply("Codice della lingua non valido.")
            return

    try:
        await message.reply_photo(f"https://art.gametdb.com/wii/coverfullHQ/{lang_code}/{id}.png")
    except:
        await message.reply("Apparentemente non esiste una copertina di questo gioco su GameTDB nella lingua specificata..")