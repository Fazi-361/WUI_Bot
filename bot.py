from dotenv import load_dotenv
load_dotenv()
from constants import init_constants
init_constants()

import os, constants as C
from traceback import format_exception
from asyncio import run
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ErrorEvent
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters.command import CommandPatternType
from aiogram.fsm.strategy import FSMStrategy
from bot_functions import *
from utils.fsm import BotState, SQLiteStorage

if not (BOT_TOKEN := os.getenv("BOT_TOKEN")): exit()
dp: Dispatcher = Dispatcher(
    storage=SQLiteStorage(),
    fsm_strategy=FSMStrategy.CHAT
)
bot: Bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
        disable_notification=True,
        allow_sending_without_reply=True
    )
)

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
        if f"@{C.BOT_USERNAME}" in text:
            new_text: str = text.replace(f"@{C.BOT_USERNAME}", "").strip()
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
    if HOST and PATH:
        await bot.set_webhook(
            url= f"{HOST}{PATH}",
            drop_pending_updates= True,
            secret_token= SECRET
        )
    else:
        await bot.delete_webhook(
            drop_pending_updates= True
        )
    
    C.BOT_USERNAME = (await bot.get_me()).username
    print(f"Bot @{C.BOT_USERNAME} started.")
    
    from json import loads
    for admin in loads(os.getenv("BOT_ADMIN") or "[]"):
        try: await bot.send_message(admin, "Bot online!")
        except: print(f"Admin {admin} suffers from skill issue.")


def main_webhook() -> None:
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    from aiohttp import web

    app = web.Application()

    SimpleRequestHandler(
        dispatcher= dp,
        bot= bot,
        secret_token= SECRET,
    ).register(app, path=PATH) # type: ignore

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=os.getenv("IP"), port=int(os.getenv("PORT"))) # type: ignore


async def main_polling() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    # Comandi
    dp.message.register(info, CustomCommand('info'))
    dp.message.register(start, CustomCommand('start'))
    dp.message.register(help, CustomCommand('help'))
    dp.message.register(echo, CustomCommand('echo'))
    dp.message.register(deid, CustomCommand('deid'))
    dp.message.register(id, CustomCommand('id'))
    dp.message.register(copertina_id, CustomCommand('copertina_id'))
    dp.message.register(lingua, CustomCommand('lingua'))
    dp.callback_query.register(set_language, BotState.language)

    # Messagi estranei
    dp.message.register(handle_message, 
        F.text,
        F.chat.type == "private"
    )

    dp.error.register(error_handler)

    if (HOST := os.getenv("WEB_HOST")) and (PATH := os.getenv("WEB_PATH")):
        from uuid import uuid4
        SECRET: str = str(uuid4())
        main_webhook()
    else:
        run(main_polling())