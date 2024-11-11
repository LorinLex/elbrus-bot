from attr import dataclass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import db_manager
from app.models import BoyModel

from app.settings import get_settings


@dataclass
class Boy:
    name: str
    call_sign: str
    tg_username: str

    @classmethod
    def from_orm(cls, model: BoyModel) -> 'Boy':
        return cls(
            name=model.name,
            call_sign=model.call_sign,
            tg_username=model.tg_username
        )


@db_manager.connection
async def add_boys(session: AsyncSession) -> None:
    boys = get_settings().boys

    for boy in boys:
        boy_row = (await session.execute(
            select(BoyModel).where(BoyModel.tg_username == boy["tg_username"])
        )).scalars().first()

        if boy_row is not None:
            continue

        session.add(BoyModel(
            name=boy["name"],
            call_sign=boy["call_sign"],
            tg_username=boy["tg_username"]
        ))
    await session.commit()


@db_manager.connection
async def get_boy(session: AsyncSession, tg_username: str) -> Boy | None:
    boy_query = select(BoyModel).where(BoyModel.tg_username == tg_username)
    row = (await session.execute(boy_query)).first()
    if row is None:
        return None
    return Boy.from_orm(row[0])
