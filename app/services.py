import datetime

from sqlalchemy import func, select

from app.models import SportActivity, Boys
from app.db import async_session

from app.settings import get_settings


class BoysService:
    @staticmethod
    async def add_boys() -> None:
        boys = get_settings().boys

        async with async_session() as session:
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


class SportService:
    async def add_report(self,
                         username: str,
                         date: datetime.date) -> None:
        async with async_session() as session:
            boy_request = select(Boys).where(Boys.tg_username == (username))
            boy = await session.execute(boy_request)

            report = SportActivity(boy=boy, date=date)

            session.add(report)
            await session.commit()

    async def get_week_stats(self):
        week = datetime.date.today().isocalendar()[1]

        async with async_session() as session:
            week_reports = select(SportActivity).\
                where(SportActivity.report_week == week).\
                join(SportActivity.boy)

            query = select(
                Boys.tg_username,
                Boys.name,
                func.count(Boys.id).label("week_reports_count")
            ).from_statement(week_reports)

            await session.execute(query)
