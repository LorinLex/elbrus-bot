from typing import Any, Awaitable, Callable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.dal import get_boy


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
