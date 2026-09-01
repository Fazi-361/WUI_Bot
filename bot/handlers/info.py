import traceback

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import I18n

from ..database import get_title_by_hash, get_title_by_name, get_title_page
from ..filters import CCommand, MessageType, T, info_botcommand, text_type
from ..utils import C, S
from ..utils.text import strim

info_router: Router = Router()


@info_router.message(CCommand(info_botcommand))
async def info_command(
    message: Message, command: CommandObject, state: FSMContext, i18n: I18n
) -> None:
    await info(message, state, command.args, i18n)


@info_router.message(
    F.chat.type == ChatType.PRIVATE,
    MessageType(T.QUERY, T.GAME_ID, T.HASH, T.MASTER_CODE),
)
async def private_message(
    message: Message, message_type: T, state: FSMContext, i18n: I18n
) -> None:
    await info(message, state, message.text, i18n, message_type)


async def info(
    message: Message,
    state: FSMContext,
    args: str | None,
    i18n: I18n,
    message_type: T | None = None,
) -> None:
    _ = i18n.gettext
    if not (args and (args := strim(args))):
        await message.reply(_("command.info.usage"))
        return

    reply: Message = await message.reply(_("info.generating"))

    try:
        user_lang: str = i18n.current_locale

        result: str | tuple[str, str, str] | None = ""
        match message_type or text_type(args):
            case T.QUERY:
                result = get_title_by_name(args, user_lang)
                enforce_title_lang: bool = False
            case T.GAME_ID:
                result = args.upper()
                enforce_title_lang = True
            case T.HASH:
                result = get_title_by_hash(args)
                enforce_title_lang = True
            case T.MASTER_CODE as m:
                result = m.data
                enforce_title_lang = True
            case _:
                raise

        assert result
        results_list: bool = isinstance(result, tuple)

        async for rich_message in get_title_page(
            _,
            await S.show_covers(state),
            result[0] if results_list else "Wii",
            result[1] if results_list else None,
            result[2] if results_list else result,
            user_lang,
            enforce_title_lang,
        ):
            await reply.edit_text(rich_message=rich_message)
    except:
        print(traceback.format_exc())
        await reply.edit_text(_("info.generation_error"))
