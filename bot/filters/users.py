from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import (
    CallbackQuery,
    ChatMemberAdministrator,
    ChatMemberOwner,
    Message,
)


class Administrator(BaseFilter):
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        try:
            chat = message.chat if isinstance(message, Message) else message.message.chat # type: ignore

            if chat.type == ChatType.PRIVATE:
                return True
            
            member = await chat.get_member(message.from_user.id) # type: ignore
            match member:
                case ChatMemberOwner():
                    return True
                case ChatMemberAdministrator():
                    return member.can_manage_chat
        except:
            pass
            
        return False