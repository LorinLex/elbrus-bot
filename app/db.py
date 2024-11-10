from typing import Awaitable, Callable, TypeVar
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, \
    AsyncAttrs, create_async_engine, AsyncEngine
from sqlalchemy.orm import DeclarativeBase

from app import settings

import logging


RT = TypeVar('RT')

logger = logging.getLogger(__name__)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class DBManager:
    engine: AsyncEngine
    session_factory: async_sessionmaker[AsyncSession]

    def __init__(self) -> None:
        self.engine = create_async_engine(settings.sqlite_path)
        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False
        )

    def connection(self, func: Callable[..., Awaitable[RT]]) \
            -> Callable[..., Awaitable[RT]]:
        async def wrapper(*args, **kwargs):
            async with self.session_factory() as session:
                logger.debug(f"ASYNC Pool: {self.engine.pool.status()}")
                return await func(session, *args, **kwargs)
        return wrapper

    async def init_models(self) -> None:
        async with self.engine.begin() as conn:
            # await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)


db_manager = DBManager()
