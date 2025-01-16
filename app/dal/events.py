
import datetime

from attr import dataclass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import db_manager
from app.models import BoyModel, EventModel


@dataclass
class Event:
    name: str
    description: str
    date_start: datetime.date
    length: int
    author_call_sign: str
    is_notified_time_left: bool
    is_repeatable: bool
    image: str


@db_manager.connection
async def add_event(
    session: AsyncSession,
    event: Event
) -> None:
    boy_query = select(BoyModel.id)\
        .where(BoyModel.call_sign == event.author_call_sign)

    event_row = EventModel(
        name=event.name,
        image=event.image,
        description=event.description,
        date_start=event.date_start,
        length=event.length,
        author=boy_query,
        is_notified_time_left=event.is_notified_time_left,
        is_repeatable=event.is_repeatable,
    )

    session.add(event_row)
    await session.commit()


@db_manager.connection
async def get_event_list(
    session: AsyncSession,
) -> list[Event]:
    query = select(
            EventModel.name,
            EventModel.image,
            EventModel.description,
            EventModel.date_start,
            EventModel.length,
            EventModel.is_notified_time_left,
            EventModel.is_repeatable,
            BoyModel.call_sign.label("author_call_sign")
        ).join(BoyModel, onclause=EventModel.author == BoyModel.id)

    result = (await session.execute(query)).all()
    return [Event(**row._mapping) for row in result]
