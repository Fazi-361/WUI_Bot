from dotenv import load_dotenv
load_dotenv()
from bot.utils.constants import init_constants
init_constants()
from bot.database import close_database

import os, bot.utils.constants as C
from traceback import format_exception
from asyncio import run
from aiogram import Bot, Dispatcher, F
from aiogram.types import BotCommand, BotCommandScopeAllChatAdministrators, BotCommandScopeAllPrivateChats, ErrorEvent
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.strategy import FSMStrategy
from aiogram.utils.i18n import I18n, FSMI18nMiddleware
from bot.bot_functions import *
from bot.handlers import ROUTERS
from bot.utils.fsm import SQLiteStorage
from bot.filters.command import CustomCommand


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
async def startup_func(*args) -> None:
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

    if not os.getenv("TESTING") or True:
        await bot.delete_my_commands()

        _ = i18n.gettext
        for locale in i18n.available_locales:
            if locale == "EN":
                continue
            
            __ = lambda singular: _(singular, locale=locale)
            language_code: str | None = None if locale == "US" else locale.lower()

            # start_command = ...
            help_command = BotCommand(command="help", description=__("command.help.description"), is_ephemeral=True)
            settings_command = BotCommand(command="settings", description=__("command.settings.description"))
            info_command = BotCommand(command="info", description=__("command.info.description"))

            await bot.set_my_commands([
                    info_command,
                ],
                language_code=language_code
            )

            for scope in {
                BotCommandScopeAllChatAdministrators,
                BotCommandScopeAllPrivateChats
            }:
                await bot.set_my_commands([
                        help_command,
                        settings_command,
                        info_command,
                    ],
                    scope=scope(),
                    language_code=language_code
                )

    print(f"Bot @{C.BOT_USERNAME} started.")

    from ast import literal_eval as eval
    for admin in eval(os.getenv("BOT_ADMIN") or "[]"):
        try: await bot.send_message(admin, "Bot online!")
        except: print(f"Admin {admin} suffers from skill issue.")


if __name__ == "__main__":
    # Middleware
    FSMI18nMiddleware(i18n := I18n(path="locales", default_locale="EN")).setup(dp)

    # Comandi
    dp.message.register(echo, CustomCommand('echo'))
    dp.message.register(deid, CustomCommand('deid'))
    dp.message.register(id, CustomCommand('id'))
    dp.message.register(copertina_id, CustomCommand('copertina_id'))

    dp.error.register(error_handler)

    # Router
    dp.include_routers(*ROUTERS)

    if (HOST := os.getenv("WEB_HOST")) and (PATH := os.getenv("WEB_PATH")):
        from uuid import uuid4
        SECRET: str = str(uuid4())
        main_webhook()
    else:
        run(main_polling())