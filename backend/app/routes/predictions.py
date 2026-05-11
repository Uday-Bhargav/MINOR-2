from fastapi import APIRouter, Depends, Query

from app.dependencies import get_repository
from app.models import Direction, SectorPrediction
from app.repository import CrisisRepository

router = APIRouter(prefix="/api/predictions", tags=["predictions"])


@router.get("", response_model=list[SectorPrediction])
async def list_predictions(
    sector: str | None = None,
    direction: Direction | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    repository: CrisisRepository = Depends(get_repository),
):
    return await repository.list_predictions(sector=sector, direction=direction, limit=limit)


@router.get("/summary")
async def prediction_summary(repository: CrisisRepository = Depends(get_repository)):
    return await repository.prediction_summary()

