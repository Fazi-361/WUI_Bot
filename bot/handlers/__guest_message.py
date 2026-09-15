import traceback
from uuid import uuid4

from aiogram import Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
    SentGuestMessage,
)
from aiogram.utils.i18n import I18n

from ..database import get_title_page
from ..utils import C, S
from ..utils.text import strim

guest_router: Router = Router()


@guest_router.guest_message()
async def guest_info(guest_message: Message, bot: Bot, state: FSMContext, i18n: I18n) -> None:    
    _ = i18n.gettext
    if not (
        (args := guest_message.text)
        and (args := strim(args.replace(f"@{C.BOT_USERNAME}", "", 1)))
    ):
        return

    reply: SentGuestMessage = await guest_message.answer_guest_query(InlineQueryResultArticle(
        id=str(uuid4()),
        title=str(uuid4()),
        input_message_content=InputTextMessageContent(message_text=_("info.generating"))
    ))

    try:
        async for *__, rich_message in get_title_page(
            i18n,
            args,
            await S.show_covers(state),
        ):
            await bot.edit_message_text(
                inline_message_id=reply.inline_message_id,
                rich_message=rich_message
            )
    except:
        print(traceback.format_exc())
        await bot.edit_message_text(
            inline_message_id=reply.inline_message_id,
            text=_("info.generation_error")
        )
