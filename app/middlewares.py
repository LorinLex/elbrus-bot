import logging
from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, \
    Chat as ChatType

from app.dal import get_boy
from app.dal.chat import Chat, add_chat, get_chat_id_list
from app.models import ChatTypeEnum


log = logging.Logger("middleware")


class ManCheckingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        boy = await get_boy(data["event_from_user"].username)
        if boy is None:
            if isinstance(event, (Message, CallbackQuery)):
                await event.answer("Ты не в списке!!11!!1")
            return

        data['boy'] = boy
        return await handler(event, data)  # type: ignore


class ChatWritingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any]
    ) -> Any:
        chat_id_list = await get_chat_id_list()
        chat_data: ChatType = data['event_chat']

        if chat_data.id not in chat_id_list:
            log.info(f"New chat: {chat_data.username}, {chat_data.title}")
            new_chat = Chat(
                id=chat_data.id,
                type=ChatTypeEnum(chat_data.type),
                title=chat_data.title,
                username=chat_data.username
            )
            await add_chat(new_chat)

        return await handler(event, data)  # type: ignore
