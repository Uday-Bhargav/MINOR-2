from collections import Counter, defaultdict
from datetime import date, datetime
import logging
from typing import Any
from uuid import UUID

import httpx

from app.config import Settings
from app.mock_data import build_demo_events
from app.models import CrisisEvent, Direction, SectorPrediction


logger = logging.getLogger(__name__)


class CrisisRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._events = build_demo_events()
        self.last_write_mode = "supabase" if settings.has_supabase else "demo-memory"

    @property
    def uses_supabase(self) -> bool:
        return self.settings.has_supabase

    def _headers(self) -> dict[str, str]:
        key = self.settings.supabase_service_role_key or ""
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def _base_url(self) -> str:
        return f"{str(self.settings.supabase_url).rstrip('/')}/rest/v1"

    async def list_events(
        self,
        category: str | None = None,
        severity: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[CrisisEvent]:
        if self.uses_supabase:
            try:
                params: list[tuple[str, str]] = [
                    ("select", "*,sector_predictions(*)"),
                    ("order", "published_at.desc"),
                    ("limit", str(limit)),
                    ("offset", str(offset)),
                ]
                if category:
                    params.append(("category", f"eq.{category}"))
                if severity:
                    params.append(("severity", f"eq.{severity}"))
                if date_from:
                    params.append(("published_at", f"gte.{date_from.isoformat()}"))
                if date_to:
                    params.append(("published_at", f"lte.{date_to.isoformat()}"))

                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(f"{self._base_url()}/crisis_events", headers=self._headers(), params=params)
                    response.raise_for_status()
                    return [self._event_from_row(row) for row in response.json()]
            except Exception as exc:
                logger.warning("Supabase list_events failed; using in-memory events instead: %s", exc)

        events = self._events
        if category:
            events = [event for event in events if event.category.value == category]
        if severity:
            events = [event for event in events if event.severity.value == severity]
        if date_from:
            events = [event for event in events if event.published_at.date() >= date_from]
        if date_to:
            events = [event for event in events if event.published_at.date() <= date_to]
        return sorted(events, key=lambda event: event.published_at, reverse=True)[offset : offset + limit]

    async def get_event(self, event_id: UUID) -> CrisisEvent | None:
        if self.uses_supabase:
            try:
                params = {"select": "*,sector_predictions(*)", "id": f"eq.{event_id}"}
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(f"{self._base_url()}/crisis_events", headers=self._headers(), params=params)
                    response.raise_for_status()
                    rows = response.json()
                    return self._event_from_row(rows[0]) if rows else None
            except Exception as exc:
                logger.warning("Supabase get_event failed; using in-memory events instead: %s", exc)
        return next((event for event in self._events if event.id == event_id), None)

    async def upsert_events(self, events: list[CrisisEvent]) -> tuple[int, int]:
        if not events:
            return (0, 0)

        if self.uses_supabase:
            try:
                event_rows = [self._event_to_row(event) for event in events]
                prediction_rows = [self._prediction_to_row(prediction) for event in events for prediction in event.predictions]
                async with httpx.AsyncClient(timeout=15) as client:
                    event_response = await client.post(
                        f"{self._base_url()}/crisis_events",
                        headers={**self._headers(), "Prefer": "resolution=merge-duplicates"},
                        json=event_rows,
                    )
                    event_response.raise_for_status()
                    if prediction_rows:
                        prediction_response = await client.post(
                            f"{self._base_url()}/sector_predictions",
                            headers={**self._headers(), "Prefer": "resolution=merge-duplicates"},
                            json=prediction_rows,
                        )
                        prediction_response.raise_for_status()
                self.last_write_mode = "supabase"
                return (len(event_rows), len(prediction_rows))
            except Exception as exc:
                logger.warning("Supabase upsert_events failed; storing events in memory instead: %s", exc)
                self.last_write_mode = "demo-memory-fallback"
                return self._upsert_memory(events)

        self.last_write_mode = "demo-memory"
        return self._upsert_memory(events)

    def _upsert_memory(self, events: list[CrisisEvent]) -> tuple[int, int]:
        existing_urls = {str(event.source_url) for event in self._events}
        new_events = [event for event in events if str(event.source_url) not in existing_urls]
        self._events = new_events + self._events
        return (len(new_events), sum(len(event.predictions) for event in new_events))

    async def list_predictions(
        self,
        sector: str | None = None,
        direction: Direction | None = None,
        limit: int = 50,
    ) -> list[SectorPrediction]:
        if self.uses_supabase:
            try:
                params: dict[str, Any] = {"select": "*", "order": "created_at.desc", "limit": str(limit)}
                if sector:
                    params["sector_name"] = f"ilike.*{sector}*"
                if direction:
                    params["direction"] = f"eq.{direction.value}"
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(f"{self._base_url()}/sector_predictions", headers=self._headers(), params=params)
                    response.raise_for_status()
                    return [SectorPrediction(**row) for row in response.json()]
            except Exception as exc:
                logger.warning("Supabase list_predictions failed; using in-memory predictions instead: %s", exc)

        predictions = [prediction for event in self._events for prediction in event.predictions]
        if sector:
            predictions = [prediction for prediction in predictions if sector.lower() in prediction.sector_name.lower()]
        if direction:
            predictions = [prediction for prediction in predictions if prediction.direction == direction]
        return sorted(predictions, key=lambda prediction: prediction.created_at, reverse=True)[:limit]

    async def search(self, query: str, limit: int = 20) -> list[CrisisEvent]:
        if self.uses_supabase:
            try:
                params = {
                    "select": "*,sector_predictions(*)",
                    "or": f"(title.ilike.*{query}*,summary.ilike.*{query}*,category.ilike.*{query}*,severity.ilike.*{query}*)",
                    "limit": str(limit),
                }
                async with httpx.AsyncClient(timeout=10) as client:
                    response = await client.get(f"{self._base_url()}/crisis_events", headers=self._headers(), params=params)
                    response.raise_for_status()
                    return [self._event_from_row(row) for row in response.json()]
            except Exception as exc:
                logger.warning("Supabase search failed; using in-memory events instead: %s", exc)

        needle = query.lower()
        results = []
        for event in self._events:
            haystack = " ".join(
                [
                    event.title,
                    event.summary,
                    event.category.value,
                    event.severity.value,
                    event.location,
                    " ".join(prediction.sector_name for prediction in event.predictions),
                ]
            ).lower()
            if needle in haystack:
                results.append(event)
        return results[:limit]

    async def prediction_summary(self) -> dict[str, Any]:
        predictions = await self.list_predictions(limit=200)
        grouped: dict[str, list[SectorPrediction]] = defaultdict(list)
        for prediction in predictions:
            grouped[prediction.sector_name].append(prediction)

        sectors = []
        for sector, items in grouped.items():
            direction_counts = Counter(item.direction.value for item in items)
            dominant_direction = direction_counts.most_common(1)[0][0]
            avg_confidence = round(sum(item.confidence for item in items) / len(items))
            sectors.append(
                {
                    "sector_name": sector,
                    "direction": dominant_direction,
                    "confidence": avg_confidence,
                    "prediction_count": len(items),
                }
            )
        return {"sectors": sorted(sectors, key=lambda item: item["confidence"], reverse=True)}

    def _event_from_row(self, row: dict[str, Any]) -> CrisisEvent:
        predictions = row.pop("sector_predictions", row.pop("predictions", [])) or []
        event = CrisisEvent(**row)
        event.predictions = [SectorPrediction(**prediction) for prediction in predictions]
        return event

    def _event_to_row(self, event: CrisisEvent) -> dict[str, Any]:
        return {
            "id": str(event.id),
            "title": event.title,
            "summary": event.summary,
            "source_url": str(event.source_url),
            "category": event.category.value,
            "severity": event.severity.value,
            "event_name": event.event_name,
            "location": event.location,
            "published_at": event.published_at.isoformat(),
            "created_at": event.created_at.isoformat(),
        }

    def _prediction_to_row(self, prediction: SectorPrediction) -> dict[str, Any]:
        return {
            "id": str(prediction.id),
            "event_id": str(prediction.event_id),
            "sector_name": prediction.sector_name,
            "direction": prediction.direction.value,
            "confidence": prediction.confidence,
            "reasoning": prediction.reasoning,
            "created_at": prediction.created_at.isoformat(),
        }
