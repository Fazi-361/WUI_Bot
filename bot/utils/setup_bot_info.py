from asyncio import sleep

from aiogram import Bot
from aiogram.types import (
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllPrivateChats,
)
from aiogram.utils.i18n import I18n

from ..filters import help_botcommand, info_botcommand, settings_botcommand


async def setup_bot_info(bot: Bot, i18n: I18n) -> None:
    _ = i18n.gettext
    for locale in i18n.available_locales:
        if locale == "EN":
            continue

        __ = lambda singular: _(singular, locale=locale)
        language_code: str | None = None if locale == "US" else locale.lower()

        # Info bot

        await bot.set_my_name(__("bot.name"), language_code)
        await bot.set_my_description(__("bot.description"), language_code)
        await bot.set_my_short_description(__("bot.short_description"), language_code)

        # Comandi

        # start_command.description = __("command.start.description"))
        help_botcommand.description = __("command.help.description")
        settings_botcommand.description = __("command.settings.description")
        info_botcommand.description = __("command.info.description")

        # Generici (non admin)
        help_botcommand.is_ephemeral = True
        settings_botcommand.is_ephemeral = True
        await bot.set_my_commands(
            commands=[
                help_botcommand,
                info_botcommand,
            ],
            language_code=language_code,
        )

        # Generici (admin)
        await bot.set_my_commands(
            commands=[
                help_botcommand,
                settings_botcommand,
                info_botcommand,
            ],
            scope=BotCommandScopeAllChatAdministrators(),
            language_code=language_code,
        )

        # Generici (chat private)
        help_botcommand.is_ephemeral = False
        settings_botcommand.is_ephemeral = False
        await bot.set_my_commands(
            commands=[
                help_botcommand,
                settings_botcommand,
                info_botcommand,
            ],
            scope=BotCommandScopeAllPrivateChats(),
            language_code=language_code,
        )

        #? Rate limit ≈ 30r/s
        await sleep(2)
