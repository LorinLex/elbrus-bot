import datetime

from attr import dataclass
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import db_manager
from app.models import SportActivityModel, BoyModel


@dataclass
class SportStats:
    call_sign: str
    sum_distance: float
    reports_count: int


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
        .filter(or_(
            SportActivityModel.report_week == week,
        ))

    result = (await session.execute(week_reports)).all()
    return [SportStats(**row._mapping) for row in result]


@db_manager.connection
async def get_month_stats(session: AsyncSession) -> list[SportStats]:
    month = datetime.date.today().strftime("%m")

    week_reports = select(
            BoyModel.call_sign,
            func.count(SportActivityModel.id).label("reports_count"),
            func.coalesce(func.sum(SportActivityModel.distance), 0)
                .label("sum_distance"))\
        .join(SportActivityModel, isouter=True)\
        .group_by(BoyModel.call_sign)\
        .filter(or_(
            func.strftime("%m", SportActivityModel.report_date) == str(month),
        ))

    result = (await session.execute(week_reports)).all()
    return [SportStats(**row._mapping) for row in result]
