from aiogram import F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated

from bot.utils.fsm import SQLiteStorage

my_chat_member_router: Router = Router()


@my_chat_member_router.my_chat_member(
    F.new_chat_member.status.in_((ChatMemberStatus.LEFT, ChatMemberStatus.KICKED))
)
async def bot_was_kicked(
    my_chat_member: ChatMemberUpdated, state: FSMContext, fsm_storage: SQLiteStorage
) -> None:
    await fsm_storage.delete(state.key)
