from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.types import Message
from aiogram.utils.i18n import I18n

message_router: Router = Router()


@message_router.message(F.chat.type == ChatType.PRIVATE)
async def handle_private_message(message: Message, i18n: I18n) -> None:
    await message.reply(i18n.gettext("query.unknown"))
