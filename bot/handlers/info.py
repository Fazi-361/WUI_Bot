from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import CommandObject
from aiogram.types import Message
from aiogram.utils.i18n import I18n

from ..database import get_title_by_hash, get_title_by_name, get_title_page
from ..filters import CCommand, MessageType, TextType as T, info_botcommand, text_type
from ..utils import constants as C
from ..utils.text import strim

info_router: Router = Router()


@info_router.message(CCommand(info_botcommand))
async def info_command(message: Message, command: CommandObject, i18n: I18n) -> None:
    await info(message, command.args or message.text, i18n)


@info_router.message(
    F.chat.type == ChatType.PRIVATE, MessageType(T.QUERY, T.GAME_ID, T.HASH)
)
async def private_message(message: Message, i18n: I18n) -> None:
    await info(message, message.text, i18n)


async def info(message: Message, args: str | None, i18n: I18n) -> None:
    _ = i18n.gettext
    if not (args and (args := strim(args))):
        await message.reply(_("command.info.usage"))
        return

    reply: Message = await message.reply(_("info.generating"))

    try:
        user_lang: str = i18n.current_locale

        result: str | tuple[str, str, str] | None = ""
        match text_type(args):
            case T.QUERY:
                result = get_title_by_name(args, C.LANG_REGIONS.get(user_lang))
                morph_lang: bool = False
            case T.GAME_ID:
                result = args.upper()
                morph_lang = True
            case T.HASH:
                result = get_title_by_hash(args)
                morph_lang = True
            case _:
                raise

        assert result
        results_list: bool = isinstance(result, tuple)

        async for rich_message in get_title_page(
            _,
            result[0] if results_list else "Wii",
            result[1] if results_list else None,
            result[2] if results_list else result,
            user_lang,
            morph_lang,
        ):
            await reply.edit_text(rich_message=rich_message)

    except Exception:
        await reply.edit_text(_("info.generation_error"))
