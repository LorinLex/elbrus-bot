from app import settings, sheduler_ins
from app.dal.events import EventDB, get_future_event_list
from app.jobs import notify_events_remaining_time, notify_tommorow_event, \
    notify_workout_week, send_everyday_joke
from apscheduler.job import Job  # type: ignore
from apscheduler.triggers.date import DateTrigger  # type: ignore


def shedule_new_event(event: EventDB) -> None:
    sheduler_ins.add_job(
        notify_tommorow_event,
        kwargs={"event_id": event.id},
        name=f"event_{event.id}_notify",
        trigger=DateTrigger(run_date=event.date_start,
                            timezone="Europe/Moscow")
    )


def modify_sheduled_event_date(updated_event: EventDB) -> None:
    job_list: list[Job] = sheduler_ins.get_jobs()

    for job in job_list:
        if job.name != f"event_{updated_event.id}_notify":
            continue

        job.modify(trigger=DateTrigger(
            run_date=updated_event.date_start,
            timezone="Europe/Moscow"
        ))


async def start_sheduler() -> None:
    sheduler_ins.add_job(
        notify_events_remaining_time,
        trigger=settings.notify_event_trigger
    )
    sheduler_ins.add_job(
        notify_workout_week,
        trigger=settings.notify_workout_week_trigger
    )

    sheduler_ins.add_job(
        send_everyday_joke,
        trigger=settings.everyday_joke_trigger
    )

    event_list = await get_future_event_list()
    for event in event_list:
        sheduler_ins.add_job(
            notify_tommorow_event,
            kwargs={"event_id": event.id},
            name=f"event_{event.id}_notify",
            trigger=DateTrigger(run_date=event.date_start,
                                timezone="Europe/Moscow")
        )

    sheduler_ins.start()
