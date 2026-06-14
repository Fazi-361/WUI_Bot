import sqlite3

from telegram import Update
from telegram.ext import ContextTypes
from jellyfish import jaro_winkler_similarity


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Avvia il bot"""
    if not update.message:
        return

    await update.message.reply_text('Bot ancora in beta! Ritorna più tardi :)')


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mostra la lista dei comandi"""
    if not update.message:
        return

    await update.message.reply_text("""Ecco una lista dei comandi:
    /start - Avvia il bot
    /help - Mostra questo menù
    /echo - Ripete la parola data
    /deid - Restituisce il gioco della Wii o Gamecube corrispondente all'ID dato.
    /id   - Restituisce l'ID di un gioco della Wii o Gamecube dato il nome.""")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ripete la frase data come argomento."""
    if not update.message:
        return

    if context.args:
        frase = " ".join(context.args)
        await update.message.reply_text(frase)
    else:
        await update.message.reply_text("Scrivi qualcosa dopo /echo! Es: /echo ciao a tutti")


async def deid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    """Data la lista di ID di giochi WII / GC, trova i nomi dei giochi corrispondenti."""
    if not update.message:
        return
    
    if not context.args:
        await update.message.reply_text("Scrivere l'ID dei giochi da cercare dopo lo /. \nesempio: /deid R8PE01 ST7P01")
        return

    game_names: list[str] = []

    for arg in context.args:
        id = arg.upper().strip()
        found = False
        with open("wiitdb.txt", "r", encoding="utf-8") as database:
            for line in database:
                # Se i primi caratteri corrispondono all'ID, aggiungere il nome del gioco a game_names
                if line[:len(id)] == id:
                    game_names.append(line[len(id)+2:].strip())
                    found = True
                    break    
            if not found:
                game_names.append(f"{id} non trovato")

    response: str = "\n".join(game_names)

    await update.message.reply_text(response)


async def deid_DB(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    """Data la lista di ID di giochi WII / GC, trova i nomi dei giochi corrispondenti."""
    if not update.message:
        return
    
    if not context.args:
        await update.message.reply_text("Scrivere l'ID dei giochi da cercare dopo lo /. \nesempio: /deid R8PE01 ST7P01")
        return

    game_names: list[str] = []

    with sqlite3.connect("./tools/database.db") as connection:
        cursor = connection.cursor()
        for arg in context.args:
            id = arg.upper().strip()
            game_name = cursor.execute(
                """SELECT gl.Title
                FROM GameLocale gl
                JOIN Game g ON gl.Game = g.MiniID
                WHERE (gl.Game || gl.Region || g.PublisherID) = ?
                LIMIT 1""",
                [id]
            ).fetchone()
            
            game_names.append(f"{id} non orato" if game_name is None else game_name[0])

    response = "\n".join(game_names)
    await update.message.reply_text(response)


async def id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Dato il nome di un gioco, restituisce l'ID del gioco corrispondente"""
    if not update.message:
        return

    if not context.args:
        await update.message.reply_text("Scrivere il nome del gioco da cercare dopo lo /. \nEsempio: /id La via della fortuna")
        return

    game_name = " ".join(context.args).strip().lower()

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
        
    await update.message.reply_text(response)