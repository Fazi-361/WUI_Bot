import os

from traceback import format_exception
from asyncio import run
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ErrorEvent
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters.command import CommandPatternType
from dotenv import load_dotenv

from bot_functions import *

load_dotenv()
if not (BOT_TOKEN := os.getenv("BOT_TOKEN")): exit()
dp: Dispatcher = Dispatcher()
bot: Bot = Bot(
    token= BOT_TOKEN,
    default= DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        disable_notification=True,
        allow_sending_without_reply=True
    )
)
BOT_USERNAME = "@tayx361_test_bot"
BOT_ADMINS: set[int] = {6028722644, 463844793}
#                       Tayx        Laxan3000

# Classe Command personalizzata per impostare i prefissi
# e le impostazioni di base per ogni comando predefinito
class CustomCommand(Command):
    def __init__(
        self,
        *values: CommandPatternType,
        commands: tuple[CommandPatternType, ...] | CommandPatternType | None = None
    ):
        super().__init__(
            *values,
            commands= commands,
            prefix= '/!.,;?',
            ignore_case= True,
            ignore_mention= False,
        )



# Risposte
def handle_responses(text: str) -> str:
    return "Non ho capito cos'hai scritto..." # ?


async def handle_message(message: Message) -> None:
    message_type: str = message.chat.type
    text: str = message.text or ''

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_responses(new_text)
        else:
            return
    else:
        response = handle_responses(text)

    await message.reply(response)


async def error_handler(event: ErrorEvent) -> bool:
    try:
        print(''.join(format_exception(
            type(event.exception),
            value= event.exception,
            tb= event.exception.__traceback__
        )))
    except:
        return False
    else:
        return True


@dp.startup()
async def startup_func(*args) -> None:
    print("Bot started.")
    for admin in BOT_ADMINS:
        try: await bot.send_message(admin, "Bot online!")
        except: pass


async def main_polling() -> None:
    await bot.delete_webhook(
        drop_pending_updates= True
    )
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Comandi
    dp.message.register(start, CustomCommand('start'))
    dp.message.register(help, CustomCommand('help'))
    dp.message.register(echo, CustomCommand('echo'))
    dp.message.register(deid, CustomCommand('deid'))
    dp.message.register(id, CustomCommand('id'))
    dp.message.register(copertina_id, CustomCommand('copertina_id'))

    # Messagi estranei
    dp.message.register(handle_message, F.text)

    dp.error.register(error_handler)

    # Long Polling
    run(main_polling())