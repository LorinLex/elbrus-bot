from datetime import datetime, date

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db import Base


class Boys(Base):
    __tablename__ = "Boys"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    call_sign: Mapped[str]
    tg_username: Mapped[str]
    sport_activity: Mapped[list["SportActivity"]] = relationship()


class SportActivity(Base):
    __tablename__ = "SportActivity"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    boy: Mapped["Boys"] = mapped_column(ForeignKey("Boys.id"))
    report_date: Mapped[date]
    report_week: Mapped[int]
    create_date: Mapped[datetime] = mapped_column(server_default=func.now())
