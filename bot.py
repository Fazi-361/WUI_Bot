import os

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

from bot_functions import *

load_dotenv()
if not (BOT_TOKEN := os.getenv("BOT_TOKEN")): exit()
BOT_USERNAME = "@tayx361_test_bot"

#                       Tayx        Laxan3000
BOT_ADMINS: set[int] = {6028722644, 463844793}


# Risposte
def handle_responses(text: str) -> str:
    return "Non ho capito cos'hai scritto..."


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    message_type: str = update.message.chat.type
    text: str = update.message.text or ''

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_responses(new_text)
        else:
            return
    else:
        response = handle_responses(text)

    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Update {update} caused error {context.error}")


async def post_init(application: Application) -> None:
    for admin in BOT_ADMINS:
        await application.bot.send_message(admin, "Bot online!")


if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # Comandi
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('echo', echo))
    app.add_handler(CommandHandler('deid', deid_DB))
    app.add_handler(CommandHandler('id', id))

    # Messagi estranei
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errori
    app.add_error_handler(error) # type: ignore

    # Long Polling
    app.run_polling(drop_pending_updates=True)