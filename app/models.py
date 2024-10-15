from datetime import datetime, date
from enum import Enum

from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db import Base


class Boys(Enum):
    KIRILL = 1
    LENYA = 2
    EMIL = 3


class SportActivity(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[Boys]
    sport_date: Mapped[date]
    create_date: Mapped[datetime] = mapped_column(server_default=func.now())
