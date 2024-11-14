
import datetime

from attr import dataclass
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import db_manager
from app.models import BoyModel, EventModel
from app.dal import Boy


@dataclass
class Event:
    name: str
    description: str
    date_start: datetime.date
    length: int
    author: Boy
    is_notified_time_left: bool
    is_repeatable: bool
    image: str


@db_manager.connection
async def add_event(
    session: AsyncSession,
    event: Event
) -> None:
    boy_query = select(BoyModel.id)\
        .where(BoyModel.tg_username == event.author.tg_username)

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
