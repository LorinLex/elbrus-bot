from datetime import datetime, date

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db import Base


class BoyModel(Base):
    __tablename__ = "BoyModel"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
    call_sign: Mapped[str]
    tg_username: Mapped[str]
    sport_activity: Mapped[list["SportActivityModel"]] = relationship()


class SportActivityModel(Base):
    __tablename__ = "SportActivityModel"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    boy: Mapped["BoyModel"] = mapped_column(ForeignKey("BoyModel.id"))
    report_date: Mapped[date]
    report_week: Mapped[int]
    distance: Mapped[float]
    create_date: Mapped[datetime] = mapped_column(server_default=func.now())
