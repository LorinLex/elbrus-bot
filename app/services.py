import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SportActivity, Boys

from app.settings import get_settings


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
                         date: datetime.date) -> None:
        boy_request = select(Boys.id).where(Boys.tg_username == (tg_username))

        report = SportActivity(boy=boy_request,
                               report_date=date,
                               report_week=date.isocalendar()[1])

        session.add(report)
        await session.commit()

    @staticmethod
    async def get_week_stats(session: AsyncSession):
        week = datetime.date.today().isocalendar()[1]

        week_reports = select(
                Boys.call_sign,
                func.count(SportActivity.id).label("week_reports_count"))\
            .join(SportActivity, isouter=True)\
            .group_by(Boys.call_sign)\
            .filter(or_(SportActivity.report_week == week,
                        SportActivity.report_week.is_(None)))

        week_stats = (await session.execute(week_reports)).all()
        return week_stats
