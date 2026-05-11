from datetime import datetime, timezone
import logging

import httpx

from app.config import Settings
from app.models import NewsArticle


CRISIS_QUERY = "(war OR conflict OR inflation OR sanctions OR energy OR disaster OR outbreak OR supply chain) markets"
logger = logging.getLogger(__name__)


class NewsService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def fetch_articles(self, limit: int = 8) -> list[NewsArticle]:
        try:
            if self.settings.news_provider == "newsapi" and self.settings.news_api_key:
                return await self._fetch_newsapi(limit)
            if self.settings.news_provider == "gnews" and self.settings.gnews_api_key:
                return await self._fetch_gnews(limit)
        except Exception as exc:
            logger.warning("News provider failed; using demo articles instead: %s", exc)
        return self._demo_articles()

    async def _fetch_newsapi(self, limit: int) -> list[NewsArticle]:
        params = {
            "q": CRISIS_QUERY,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": limit,
            "apiKey": self.settings.news_api_key,
        }
        async with httpx.AsyncClient(timeout=12) as client:
            response = await client.get("https://newsapi.org/v2/everything", params=params)
            response.raise_for_status()
        return [
            NewsArticle(
                title=item.get("title") or "Untitled",
                source=(item.get("source") or {}).get("name") or "Unknown",
                source_url=item.get("url") or "",
                published_at=_parse_datetime(item.get("publishedAt")),
                description=item.get("description") or "",
                content=item.get("content") or "",
            )
            for item in response.json().get("articles", [])
            if item.get("url")
        ]

    async def _fetch_gnews(self, limit: int) -> list[NewsArticle]:
        params = {
            "q": CRISIS_QUERY,
            "lang": "en",
            "max": limit,
            "apikey": self.settings.gnews_api_key,
        }
        async with httpx.AsyncClient(timeout=12) as client:
            response = await client.get("https://gnews.io/api/v4/search", params=params)
            response.raise_for_status()
        return [
            NewsArticle(
                title=item.get("title") or "Untitled",
                source=(item.get("source") or {}).get("name") or "Unknown",
                source_url=item.get("url") or "",
                published_at=_parse_datetime(item.get("publishedAt")),
                description=item.get("description") or "",
                content=item.get("content") or "",
            )
            for item in response.json().get("articles", [])
            if item.get("url")
        ]

    def _demo_articles(self) -> list[NewsArticle]:
        now = datetime.now(timezone.utc)
        return [
            NewsArticle(
                title="Oil prices climb as port strike disrupts fuel shipments",
                source="Demo Wire",
                source_url="https://example.com/demo/oil-port-strike",
                published_at=now,
                description="A port strike has delayed refined fuel shipments and raised concerns about near-term supply.",
                content="Energy traders are watching inventory levels as shipping delays affect regional fuel availability.",
            ),
            NewsArticle(
                title="Food exporters face restrictions after drought damages crops",
                source="Demo Wire",
                source_url="https://example.com/demo/drought-food-exports",
                published_at=now,
                description="Drought conditions have damaged crops and prompted emergency export controls.",
                content="Agriculture, food retail, and fertilizer names are expected to react as supply forecasts tighten.",
            ),
        ]


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
