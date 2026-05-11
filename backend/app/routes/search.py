from fastapi import APIRouter, Depends, Query

from app.dependencies import get_repository
from app.models import CrisisEvent
from app.repository import CrisisRepository

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=list[CrisisEvent])
async def search_events(
    q: str = Query(min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    repository: CrisisRepository = Depends(get_repository),
):
    return await repository.search(q, limit=limit)

