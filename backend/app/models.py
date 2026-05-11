from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class Category(str, Enum):
    geopolitical = "Geopolitical"
    economic = "Economic"
    natural_disaster = "Natural Disaster"
    energy = "Energy"
    health = "Health"


class Severity(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class Direction(str, Enum):
    rise = "rise"
    fall = "fall"
    neutral = "neutral"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SectorPrediction(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    event_id: UUID
    sector_name: str
    direction: Direction
    confidence: int = Field(ge=0, le=100)
    reasoning: str
    created_at: datetime = Field(default_factory=utc_now)


class CrisisEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    summary: str
    source_url: HttpUrl | str
    category: Category
    severity: Severity
    event_name: str
    location: str
    published_at: datetime
    created_at: datetime = Field(default_factory=utc_now)
    predictions: list[SectorPrediction] = Field(default_factory=list)


class NewsArticle(BaseModel):
    title: str
    source: str
    source_url: HttpUrl | str
    published_at: datetime
    description: str = ""
    content: str = ""

