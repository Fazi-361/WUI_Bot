import traceback

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.i18n import I18n

from ..database import get_title_page
from ..filters import CCommand, MessageType, T, info_botcommand
from ..utils import S
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
        async for rich_message in get_title_page(
            _, args, i18n.current_locale, await S.show_covers(state), message_type
        ):
            await reply.edit_text(rich_message=rich_message)
    except:
        print(traceback.format_exc())
        await reply.edit_text(_("info.generation_error"))
