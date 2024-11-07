import datetime

from attr import dataclass
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import db_manager
from app.models import SportActivityModel, BoyModel

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


@dataclass
class SportStats:
    call_sign: str
    sum_distance: float
    reports_count: int


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


@db_manager.connection
async def add_report(
    session: AsyncSession,
    tg_username: str,
    date: datetime.date,
    distance: float
) -> None:
    boy_request = select(BoyModel.id)\
        .where(BoyModel.tg_username == tg_username)

    report = SportActivityModel(
        boy=boy_request,
        report_date=date,
        report_week=date.isocalendar()[1],
        distance=distance
    )

    session.add(report)
    await session.commit()


@db_manager.connection
async def get_week_stats(session: AsyncSession) -> list[SportStats]:
    week = datetime.date.today().isocalendar()[1]

    week_reports = select(
            BoyModel.call_sign,
            func.count(SportActivityModel.id).label("reports_count"),
            func.coalesce(func.sum(SportActivityModel.distance), 0)
                .label("sum_distance"))\
        .join(SportActivityModel, isouter=True)\
        .group_by(BoyModel.call_sign)\
        .filter(or_(SportActivityModel.report_week == week,
                    SportActivityModel.report_week.is_(None)))

    result = (await session.execute(week_reports)).all()
    return [SportStats(**row._mapping) for row in result]


@db_manager.connection
async def get_month_stats(session: AsyncSession) -> list[SportStats]:
    month = datetime.date.today().month

    week_reports = select(
            BoyModel.call_sign,
            func.count(SportActivityModel.id).label("reports_count"),
            func.coalesce(func.sum(SportActivityModel.distance), 0)
                .label("sum_distance"))\
        .join(SportActivityModel, isouter=True)\
        .group_by(BoyModel.call_sign)\
        .filter(or_(
            func.strftime("%m", SportActivityModel.report_date) == str(month),
            SportActivityModel.report_date.is_(None)
        ))

    result = (await session.execute(week_reports)).all()
    return [SportStats(**row._mapping) for row in result]
