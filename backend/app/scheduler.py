from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import Settings
from app.services.processor import CrisisProcessor


def build_scheduler(settings: Settings, processor: CrisisProcessor) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        processor.fetch_and_process,
        "interval",
        minutes=settings.refresh_minutes,
        id="fetch-crisis-news",
        replace_existing=True,
        max_instances=1,
    )
    return scheduler

