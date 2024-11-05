import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SportActivity, Boys

from app.settings import get_settings


ELBRUS_HEIGHT: float = 5.642


class BoysService:
    @staticmethod
    async def add_boys(session: AsyncSession) -> None:
        boys = get_settings().boys

        for boy in boys:
            boy_row = (await session.execute(
                select(Boys).where(Boys.tg_username == boy["tg_username"])
            )).scalars().first()

            if boy_row is not None:
                continue

            session.add(Boys(
                name=boy["name"],
                call_sign=boy["call_sign"],
                tg_username=boy["tg_username"]
            ))
        await session.commit()

    @staticmethod
    async def get_boy(session: AsyncSession, tg_username: str):
        boy_query = select(Boys).where(Boys.tg_username == tg_username)
        return (await session.execute(boy_query)).scalars().first()


class SportService:
    @staticmethod
    async def add_report(session: AsyncSession,
                         tg_username: str,
                         date: datetime.date,
                         distance: float) -> None:
        boy_request = select(Boys.id).where(Boys.tg_username == (tg_username))

        report = SportActivity(boy=boy_request,
                               report_date=date,
                               report_week=date.isocalendar()[1],
                               distance=distance)

        session.add(report)
        await session.commit()

    @staticmethod
    async def get_week_stats(session: AsyncSession):
        week = datetime.date.today().isocalendar()[1]

        week_reports = select(
                Boys.call_sign,
                func.count(SportActivity.id).label("reports_count"),
                func.coalesce(func.sum(SportActivity.distance), 0)
                    .label("sum_distance"))\
            .join(SportActivity, isouter=True)\
            .group_by(Boys.call_sign)\
            .filter(or_(SportActivity.report_week == week,
                        SportActivity.report_week.is_(None)))

        result = (await session.execute(week_reports)).all()
        return [row._mapping for row in result]

    @staticmethod
    async def get_month_stats(session: AsyncSession):
        month = datetime.date.today().month

        week_reports = select(
                Boys.call_sign,
                func.count(SportActivity.id).label("reports_count"),
                func.coalesce(func.sum(SportActivity.distance), 0)
                    .label("sum_distance"))\
            .join(SportActivity, isouter=True)\
            .group_by(Boys.call_sign)\
            .filter(or_(
                func.strftime("%m", SportActivity.report_date) == str(month),
                SportActivity.report_date.is_(None)
            ))

        result = (await session.execute(week_reports)).all()
        return [row._mapping for row in result]

    @staticmethod
    def in_elbrus_height(dist: float | int) -> float:
        return round(dist / ELBRUS_HEIGHT * 100, 2)
