from functools import lru_cache

from app.config import get_settings
from app.repository import CrisisRepository
from app.services.ai import AIAnalysisService
from app.services.news import NewsService
from app.services.processor import CrisisProcessor


@lru_cache
def get_repository() -> CrisisRepository:
    return CrisisRepository(get_settings())


@lru_cache
def get_ai_service() -> AIAnalysisService:
    return AIAnalysisService(get_settings())


@lru_cache
def get_news_service() -> NewsService:
    return NewsService(get_settings())


def get_processor() -> CrisisProcessor:
    return CrisisProcessor(get_news_service(), get_ai_service(), get_repository())

