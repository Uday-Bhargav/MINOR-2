from fastapi import APIRouter, Depends

from app.dependencies import get_ai_service, get_repository
from app.repository import CrisisRepository
from app.schemas import ChatRequest, ChatResponse
from app.services.ai import AIAnalysisService

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    repository: CrisisRepository = Depends(get_repository),
    ai_service: AIAnalysisService = Depends(get_ai_service),
):
    events = await repository.search(request.message, limit=6)
    if not events:
        events = await repository.list_events(limit=6)
    context = "\n\n".join(
        [
            f"Event: {event.event_name}\nTitle: {event.title}\nSummary: {event.summary}\nPredictions: "
            + "; ".join(
                f"{prediction.sector_name} {prediction.direction.value} ({prediction.confidence}%): {prediction.reasoning}"
                for prediction in event.predictions
            )
            for event in events
        ]
    )
    answer = await ai_service.answer_chat(request.message, context)
    return ChatResponse(answer=answer, sources=[event.id for event in events])

