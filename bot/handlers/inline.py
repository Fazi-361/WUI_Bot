import traceback
from uuid import uuid4

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultsButton,
    InputRichMessageContent,
)
from aiogram.utils.i18n import I18n

from ..database import get_title_page
from ..filters import MessageType, T
from ..utils import S
from ..utils.text import strim

inline_router: Router = Router()


@inline_router.inline_query(MessageType(T.QUERY, T.GAME_ID, T.HASH, T.MASTER_CODE))
async def inline_info(inline_query: InlineQuery, state: FSMContext, message_type: T, i18n: I18n):
    _ = i18n.gettext
    try:
        title_name, front_cover, rich_message = await anext(
            iterator := get_title_page(
                i18n, strim(inline_query.query), await S.show_covers(state), message_type
            )
        )
        # Salta fino l'ultima iterazione
        async for title_name, front_cover, rich_message in iterator:
            pass
    except:
        print(traceback.format_exc())
        return inline_query.answer(
            results=[],
            button=InlineQueryResultsButton(
                text=_("info.generation_error"), start_parameter="_"
            ),
        )
    else:
        return inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=title_name,
                    input_message_content=InputRichMessageContent(
                        rich_message=rich_message
                    ),
                    thumbnail_url=front_cover,
                ),
            ],
            is_personal=True,
        )
