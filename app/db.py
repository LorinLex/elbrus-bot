from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.settings import get_settings


class Base(AsyncAttrs, DeclarativeBase):
    pass


def get_sessionmaker():
    engine = create_async_engine(get_settings().sqlite_path)

    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    return async_session_maker
