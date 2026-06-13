from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from jellyfish import jaro_winkler_similarity

import os


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "@tayx361_test_bot"


#### COMANDI ####

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Avvia il bot"""
    
    await update.message.reply_text('Hello! Welcome!')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mostra la lista dei comandi"""

    await update.message.reply_text("""Ecco una lista dei comandi:
    /start - Avvia il bot
    /help - Mostra questo menù
    /echo - Ripete la parola data
    /deid - Restituisce il gioco della Wii o Gamecube corrispondente all'ID dato.""")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ripete la frase data come argomento."""

    if context.args:
        frase = " ".join(context.args)
        await update.message.reply_text(frase)
    else:
        await update.message.reply_text("Scrivi qualcosa dopo /echo! Es: /echo ciao a tutti")

async def deid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Data la lista di ID di giochi WII / GC, trova i nomi dei giochi corrispondenti."""
    
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


async def id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dato il nome di un gioco, restituisce l'ID del gioco corrispondente"""
    if not context.args:
        await update.message.reply_text("Scrivere il nome del gioco da cercare dopo lo /. \nEsempio: /id La via della fortuna")
        return

    game_name = " ".join(context.args).strip().lower()
    print(game_name)
    id = ""

    best_similarity: float = 0
    best_id: str = ""    
    with open("wiitdb.txt", "r", encoding="utf-8") as database:
        for line in database:
            line_game_name = line[9:].lower().strip()
            similarity = jaro_winkler_similarity(game_name, line_game_name)
            if similarity > best_similarity:
                best_similarity = similarity
                best_id = line[:6].removesuffix("=").strip()

    response: str = ""
    if best_similarity > 0.8:
        response = best_id
    else:
        response = "Gioco non trovato"
        
    await update.message.reply_text(response)
        

# Risposte

def handle_responses(text: str) -> str:
    return "Non ho capito cos'hai scritto..."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f"User ({update.message.chat.id}) in {message_type}: \"{text}\"")

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_responses(new_text)
        else:
            return
    else:
        response: str = handle_responses(text)
    
    print("Bot:", response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")


if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()

    # Comandi
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('echo', echo))
    app.add_handler(CommandHandler('deid', deid))
    app.add_handler(CommandHandler('id', id))

    # Messagi estranei
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errori
    app.add_error_handler(error)

    # Long Polling
    print("Polling...")
    app.run_polling()