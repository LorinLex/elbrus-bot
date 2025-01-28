from datetime import datetime, date
from enum import Enum
from typing import Optional

from sqlalchemy import Column, ForeignKey, Table, func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db import Base


class ChatTypeEnum(Enum):
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"


BoyEventModel = Table(
    "BoyEventModel",
    Base.metadata,
    Column("boy_id", ForeignKey("BoyModel.id"), primary_key=True),
    Column("event_id", ForeignKey("EventModel.id"), primary_key=True),
)


class BoyModel(Base):
    __tablename__ = "BoyModel"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    call_sign: Mapped[str]
    tg_username: Mapped[str]
    sport_activity: Mapped[list["SportActivityModel"]] = relationship()
    events: Mapped[list["EventModel"]] = relationship(
        secondary=BoyEventModel,
        back_populates="members"
    )


class SportActivityModel(Base):
    __tablename__ = "SportActivityModel"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    boy: Mapped["BoyModel"] = mapped_column(ForeignKey("BoyModel.id"))
    report_date: Mapped[date]
    report_week: Mapped[int]
    distance: Mapped[float]
    create_date: Mapped[datetime] = mapped_column(server_default=func.now())


class EventModel(Base):
    __tablename__ = "EventModel"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    image: Mapped[str]
    description: Mapped[str]
    date_start: Mapped[date]
    length: Mapped[int]
    members: Mapped[list["BoyModel"]] = relationship(
        secondary=BoyEventModel,
        back_populates="events"
    )
    author: Mapped["BoyModel"] = mapped_column(ForeignKey("BoyModel.id"))
    is_notified_time_left: Mapped[bool] = mapped_column(default=False)
    is_repeatable: Mapped[bool] = mapped_column(default=False)
    create_date: Mapped[datetime] = mapped_column(server_default=func.now())


class ChatModel(Base):
    __tablename__ = "ChatModel"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[ChatTypeEnum]
    title: Mapped[Optional[str]]
    username: Mapped[Optional[str]]
