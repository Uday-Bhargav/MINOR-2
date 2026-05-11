from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from app.dependencies import get_processor, get_repository
from app.models import Category, CrisisEvent, Severity
from app.repository import CrisisRepository
from app.schemas import FetchResponse
from app.services.processor import CrisisProcessor

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=list[CrisisEvent])
async def list_events(
    category: Category | None = None,
    severity: Severity | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    repository: CrisisRepository = Depends(get_repository),
):
    return await repository.list_events(
        category=category.value if category else None,
        severity=severity.value if severity else None,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )


@router.get("/{event_id}", response_model=CrisisEvent)
async def get_event(event_id: UUID, repository: CrisisRepository = Depends(get_repository)):
    event = await repository.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/fetch", response_model=FetchResponse)
async def fetch_events(processor: CrisisProcessor = Depends(get_processor), repository: CrisisRepository = Depends(get_repository)):
    created_events, created_predictions, _ = await processor.fetch_and_process()
    return FetchResponse(
        created_events=created_events,
        created_predictions=created_predictions,
        mode=repository.last_write_mode,
    )
