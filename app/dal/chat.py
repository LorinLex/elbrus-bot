from sqlalchemy import select
from app import settings
from app.db import db_manager
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import ChatModel, ChatTypeEnum
from dataclasses import dataclass


@dataclass
class Chat:
    id: int
    type: ChatTypeEnum
    username: str | None
    title: str | None


@db_manager.connection
async def get_chat_id_list(session: AsyncSession):
    query = select(ChatModel.id)
    result = await session.execute(query)
    return result.scalars().all()


@db_manager.connection
async def get_chat_group_id_list(session: AsyncSession):
    query = select(ChatModel.id)\
        .where(ChatModel.type == ChatTypeEnum.GROUP)
    result = await session.execute(query)
    return result.scalars()


def get_main_group_id():
    return settings.main_group_id


@db_manager.connection
async def add_chat(session: AsyncSession, chat: Chat):
    chat_row = ChatModel(
        id=chat.id,
        type=chat.type,
        username=chat.username,
        title=chat.title
    )

    session.add(chat_row)
    await session.commit()
