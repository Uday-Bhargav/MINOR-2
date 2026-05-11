from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field

from app.models import Category, Direction, Severity


class EventFilters(BaseModel):
    category: Category | None = None
    severity: Severity | None = None
    date_from: date | None = None
    date_to: date | None = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PredictionFilters(BaseModel):
    sector: str | None = None
    direction: Direction | None = None
    limit: int = Field(default=50, ge=1, le=200)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    answer: str
    sources: list[UUID] = []


class FetchResponse(BaseModel):
    created_events: int
    created_predictions: int
    mode: str

