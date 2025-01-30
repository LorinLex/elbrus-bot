import logging
from sqlalchemy import select
from app.db import db_manager
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import ChatModel, ChatTypeEnum
from dataclasses import dataclass


logger = logging.getLogger("dal:chat")


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


@db_manager.connection
async def get_main_group_id(session: AsyncSession):
    query = select(ChatModel.id)\
        .where(ChatModel.title == "Бооооооооутишки Inc.")
    result = await session.execute(query)
    id = result.scalars().first()
    if not id:
        logger.critical("No 'Бооооооооутишки Inc.' group in db!!!")
        raise NoResultFound()
    return id


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
