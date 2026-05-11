import asyncio

from app.models import CrisisEvent
from app.repository import CrisisRepository
from app.services.ai import AIAnalysisService
from app.services.news import NewsService


class CrisisProcessor:
    def __init__(self, news_service: NewsService, ai_service: AIAnalysisService, repository: CrisisRepository):
        self.news_service = news_service
        self.ai_service = ai_service
        self.repository = repository

    async def fetch_and_process(self) -> tuple[int, int, list[CrisisEvent]]:
        articles = await self.news_service.fetch_articles()
        events = await asyncio.gather(*(self.ai_service.analyze_article(article) for article in articles))
        created_events, created_predictions = await self.repository.upsert_events(events)
        return created_events, created_predictions, events

