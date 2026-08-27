from asyncio import sleep

from aiogram import Bot
from aiogram.types import (
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllPrivateChats,
)
from aiogram.utils.i18n import I18n

from ..filters.commands import *


async def setup_bot_info(bot: Bot, i18n: I18n) -> None:
    _ = i18n.gettext
    default_locale = i18n.default_locale

    bot_name_key: str = "bot.name"
    bot_name_def: str = _(bot_name_key, locale=default_locale)
    for locale in i18n.available_locales:
        if locale == "EN":
            continue

        print("Setting bot info for", locale)

        __ = lambda singular: _(singular, locale=locale)
        language_code: str | None = locale.lower() if locale != default_locale else None

        # * Info bot

        try:
            if bot_name_def != (new_name := __("bot.name")):
                await bot.set_my_name(new_name, language_code)
        except:
            pass

        await bot.set_my_description(__("bot.description"), language_code)
        await bot.set_my_short_description(__("bot.short_description"), language_code)

        # * Comandi

        for command in BOTCOMMANDS:
            command.description = __(f"command.{command.command}.description")

        # Gruppi

        help_botcommand.is_ephemeral = True
        settings_botcommand.is_ephemeral = True

        # Gruppi: non admin
        await bot.set_my_commands(
            commands=[
                help_botcommand,
                info_botcommand,
                deid_botcommand,
                id_botcommand
            ],
            language_code=language_code,
        )

        # Gruppi: admin
        await bot.set_my_commands(
            commands=[
                help_botcommand,
                settings_botcommand,
                info_botcommand,
                deid_botcommand,
                id_botcommand
            ],
            scope=BotCommandScopeAllChatAdministrators(),
            language_code=language_code,
        )

        # Chat private

        help_botcommand.is_ephemeral = False
        settings_botcommand.is_ephemeral = False

        await bot.set_my_commands(
            commands=[
                help_botcommand,
                settings_botcommand,
                info_botcommand,
                deid_botcommand,
                id_botcommand
            ],
            scope=BotCommandScopeAllPrivateChats(),
            language_code=language_code,
        )

        # ? Rate limit ≈ 30r/s
        await sleep(2)

    # Ripristina la descrizione dei comandi
    for command in BOTCOMMANDS:
        command.description = f"command.{command.command}.description"
        
    print("Bot info set without errors!")
