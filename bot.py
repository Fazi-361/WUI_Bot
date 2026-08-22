from asyncio import run, create_task
import os
from traceback import format_exception

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import ErrorEvent
from aiogram.utils.i18n import FSMI18nMiddleware, I18n
from dotenv import load_dotenv

from bot.bot_functions import *
from bot.database import close_database
from bot.filters import CCommand
from bot.handlers import ROUTERS
from bot.utils import constants as C, setup_bot_info
from bot.utils.fsm import SQLiteStorage
load_dotenv()


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


async def error_handler(event: ErrorEvent) -> bool:
    try:
        print(''.join(format_exception(
            type(event.exception),
            value=event.exception,
            tb=event.exception.__traceback__
        )))
    except:
        return False
    else:
        return True


def main_webhook() -> None:
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
    from aiohttp import web

    app = web.Application()

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=SECRET,
    ).register(app, path=PATH) # type: ignore

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=os.getenv("IP"), port=int(os.getenv("PORT"))) # type: ignore


async def main_polling() -> None:
    await dp.start_polling(bot)


@dp.shutdown()
async def shutdown_func(*args) -> None:
    close_database()


@dp.startup()
async def startup_func() -> None:
    from ast import literal_eval as eval

    if HOST and PATH:
        await bot.set_webhook(
            url=f"{HOST}{PATH}",
            drop_pending_updates=True,
            secret_token=SECRET
        )
    else:
        await bot.delete_webhook(
            drop_pending_updates=True
        )

    C.BOT_USERNAME = (await bot.get_me()).username
    C.BOT_CREATORS = eval(os.getenv("BOT_ADMIN") or "[]")

    if not os.getenv("TESTING"):
        create_task(setup_bot_info(bot, i18n))

    print(f"Bot @{C.BOT_USERNAME} started.")

    for admin in C.BOT_CREATORS:
        try: await bot.send_message(admin, "Bot online!")
        except: print(f"Admin {admin} suffers from skill issue.")


if __name__ == "__main__":
    # Middleware
    FSMI18nMiddleware(i18n := I18n(path="locales", default_locale="EN")).setup(dp)

    dp.error.register(error_handler)

    # Router
    dp.include_routers(*ROUTERS)

    if (HOST := os.getenv("WEB_HOST")) and (PATH := os.getenv("WEB_PATH")):
        from uuid import uuid4
        SECRET: str = str(uuid4())
        main_webhook()
    else:
        run(main_polling())