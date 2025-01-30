import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import db_manager
from app.models import BoyModel, EventModel

from dataclasses import dataclass


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


@dataclass
class EventDB(Event):
    id: int


event_query = select(
    EventModel.id,
    EventModel.name,
    EventModel.image,
    EventModel.description,
    EventModel.date_start,
    EventModel.length,
    EventModel.is_notified_time_left,
    EventModel.is_repeatable,
    BoyModel.call_sign.label("author_call_sign")
).join(BoyModel, onclause=EventModel.author == BoyModel.id)


@db_manager.connection
async def add_event(
    session: AsyncSession,
    event: Event
) -> None:
    boy_query = select(BoyModel.id)\
        .where(BoyModel.call_sign == event.author_call_sign)

    event_raw = EventModel(
        name=event.name,
        image=event.image,
        description=event.description,
        date_start=event.date_start,
        length=event.length,
        author=boy_query,
        is_notified_time_left=event.is_notified_time_left,
        is_repeatable=event.is_repeatable,
    )

    session.add(event_raw)
    await session.commit()


@db_manager.connection
async def update_event(
    session: AsyncSession,
    event_id: int,
    **kwargs
) -> None:
    query = update(EventModel)\
        .where(EventModel.id == event_id)\
        .values(**kwargs)

    await session.execute(query)
    await session.commit()


@db_manager.connection
async def get_event_list(
    session: AsyncSession,
) -> list[EventDB]:
    result = (await session.execute(event_query)).all()
    return [EventDB(**row._mapping) for row in result]


@db_manager.connection
async def get_notifying_event_list(
    session: AsyncSession,
) -> list[EventDB]:
    query = event_query.where(
        EventModel.is_notified_time_left,
        EventModel.date_start > datetime.date.today()
    )

    result = (await session.execute(query)).all()
    return [EventDB(**row._mapping) for row in result]


@db_manager.connection
async def get_future_event_list(session: AsyncSession) -> list[EventDB]:
    query = event_query.where(EventModel.date_start > datetime.date.today())
    result = (await session.execute(query)).all()
    return [EventDB(**row._mapping) for row in result]


@db_manager.connection
async def get_event_by_id(session: AsyncSession, id: int) -> EventDB:
    query = event_query.where(EventModel.id == id)

    result = (await session.execute(query)).first()
    if result is None:
        raise NoResultFound()
    return EventDB(**result._mapping)


@db_manager.connection
async def get_event_by_name(session: AsyncSession, name: str) -> EventDB:
    query = event_query.where(EventModel.name == name)

    result = (await session.execute(query)).first()
    if result is None:
        raise NoResultFound()
    return EventDB(**result._mapping)


@db_manager.connection
async def delete_event(session: AsyncSession, event_id: int) -> None:
    query = delete(EventModel).where(EventModel.id == event_id)
    await session.execute(query)
    await session.commit()
