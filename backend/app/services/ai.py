import json
import logging
from uuid import uuid4

import httpx

from app.config import Settings
from app.models import Category, CrisisEvent, Direction, NewsArticle, SectorPrediction, Severity


SYSTEM_PROMPT = """You are a financial crisis market analyst.
Return strict JSON with keys: event_name, location, category, severity, summary, predictions.
category must be one of: Geopolitical, Economic, Natural Disaster, Energy, Health.
severity must be one of: Low, Medium, High.
summary must be exactly three concise sentences.
predictions is an array of objects: sector_name, direction, confidence, reasoning.
direction must be rise, fall, or neutral. confidence is 0 to 100. reasoning is 2-3 sentences."""
logger = logging.getLogger(__name__)


class AIAnalysisService:
    def __init__(self, settings: Settings):
        self.settings = settings

    async def analyze_article(self, article: NewsArticle) -> CrisisEvent:
        try:
            if self.settings.ai_provider == "openai" and self.settings.openai_api_key:
                payload = await self._openai(article)
            elif self.settings.ai_provider == "anthropic" and self.settings.anthropic_api_key:
                payload = await self._anthropic(article)
            elif self.settings.ai_provider == "groq" and self.settings.groq_api_key:
                payload = await self._groq(article)
            else:
                payload = self._demo_analysis(article)
        except Exception as exc:
            logger.warning("AI provider failed; using demo analysis for article %r: %s", article.title, exc)
            payload = self._demo_analysis(article)
        return self._event_from_payload(article, payload)

    async def answer_chat(self, message: str, context: str) -> str:
        if self.settings.ai_provider == "openai" and self.settings.openai_api_key:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                    json={
                        "model": self.settings.openai_model,
                        "messages": [
                            {"role": "system", "content": "Answer using only the supplied crisis market context. Be concise and cite event names."},
                            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {message}"},
                        ],
                    },
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        if self.settings.ai_provider == "groq" and self.settings.groq_api_key:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.settings.groq_api_key}"},
                    json={
                        "model": self.settings.groq_model,
                        "messages": [
                            {"role": "system", "content": "Answer using only the supplied crisis market context. Be concise and cite event names."},
                            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {message}"},
                        ],
                    },
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        if self.settings.ai_provider == "anthropic" and self.settings.anthropic_api_key:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.settings.anthropic_api_key,
                        "anthropic-version": "2023-06-01",
                    },
                    json={
                        "model": self.settings.anthropic_model,
                        "max_tokens": 600,
                        "system": "Answer using only the supplied crisis market context. Be concise and cite event names.",
                        "messages": [{"role": "user", "content": f"Context:\n{context}\n\nQuestion: {message}"}],
                    },
                )
                response.raise_for_status()
                return response.json()["content"][0]["text"]
        return self._demo_chat(message, context)

    async def _openai(self, article: NewsArticle) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                json={
                    "model": self.settings.openai_model,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": self._article_prompt(article)},
                    ],
                },
            )
            response.raise_for_status()
            return json.loads(response.json()["choices"][0]["message"]["content"])

    async def _anthropic(self, article: NewsArticle) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                },
                json={
                    "model": self.settings.anthropic_model,
                    "max_tokens": 900,
                    "system": SYSTEM_PROMPT,
                    "messages": [{"role": "user", "content": self._article_prompt(article)}],
                },
            )
            response.raise_for_status()
            return json.loads(response.json()["content"][0]["text"])

    async def _groq(self, article: NewsArticle) -> dict:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.settings.groq_api_key}"},
                json={
                    "model": self.settings.groq_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                            + "\nReturn ONLY raw JSON. No markdown, no backticks. No newlines inside string values.",
                        },
                        {"role": "user", "content": self._article_prompt(article)},
                    ],
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            content = content.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            content = "".join(char if char in "\n\r\t" or ord(char) >= 32 else " " for char in content)
            return json.loads(content)

    def _article_prompt(self, article: NewsArticle) -> str:
        return f"Title: {article.title}\nSource: {article.source}\nDescription: {article.description}\nContent: {article.content}"

    def _event_from_payload(self, article: NewsArticle, payload: dict) -> CrisisEvent:
        event_id = uuid4()
        event = CrisisEvent(
            id=event_id,
            title=article.title,
            event_name=payload.get("event_name") or article.title[:80],
            location=payload.get("location") or "Global",
            category=self._enum_value(Category, payload.get("category"), Category.economic),
            severity=self._enum_value(Severity, payload.get("severity"), Severity.medium),
            summary=payload.get("summary") or article.description or article.title,
            source_url=article.source_url,
            published_at=article.published_at,
        )
        predictions = payload.get("predictions", [])
        if not isinstance(predictions, list):
            predictions = []
        event.predictions = [
            SectorPrediction(
                event_id=event_id,
                sector_name=item.get("sector_name", "Broad Market"),
                direction=self._enum_value(Direction, item.get("direction"), Direction.neutral),
                confidence=self._confidence(item.get("confidence", 50)),
                reasoning=item.get("reasoning", "The event may influence investor risk appetite and sector positioning."),
            )
            for item in predictions
            if isinstance(item, dict)
        ]
        return event

    def _enum_value(self, enum_type, value, default):
        try:
            return enum_type(value or default.value)
        except (TypeError, ValueError):
            return default

    def _confidence(self, value) -> int:
        try:
            confidence = int(value)
        except (TypeError, ValueError):
            confidence = 50
        return max(0, min(100, confidence))

    def _demo_analysis(self, article: NewsArticle) -> dict:
        text = f"{article.title} {article.description}".lower()
        if any(term in text for term in ["oil", "fuel", "energy", "gas"]):
            return {
                "event_name": "Energy Supply Disruption",
                "location": "Global",
                "category": "Energy",
                "severity": "High",
                "summary": "A supply disruption is creating stress in fuel logistics and pricing. Energy producers may benefit from tighter supply while fuel-intensive sectors face margin pressure. The market impact should persist until shipping flows and inventories normalize.",
                "predictions": [
                    {"sector_name": "Oil & Gas", "direction": "rise", "confidence": 84, "reasoning": "Supply constraints can lift crude and refined product prices. Producers and integrated energy companies often benefit when pricing power improves."},
                    {"sector_name": "Airlines", "direction": "fall", "confidence": 76, "reasoning": "Fuel is a major airline expense, so price spikes pressure margins. Demand can also soften if ticket prices rise."},
                    {"sector_name": "Transport", "direction": "fall", "confidence": 70, "reasoning": "Trucking and logistics companies face higher operating costs. Contract pricing may lag spot fuel moves, pressuring profitability."},
                ],
            }
        return {
            "event_name": "Macro Crisis Event",
            "location": "Global",
            "category": "Economic",
            "severity": "Medium",
            "summary": "A crisis event is changing expectations for growth, inflation, and investor risk appetite. Defensive sectors may hold up better while cyclical sectors face uncertainty. Market direction will depend on how quickly the disruption is contained.",
            "predictions": [
                {"sector_name": "Consumer Staples", "direction": "rise", "confidence": 64, "reasoning": "Defensive demand can attract capital during uncertainty. Staples companies are often less exposed to economic swings."},
                {"sector_name": "Industrials", "direction": "fall", "confidence": 61, "reasoning": "Industrial firms can be vulnerable to supply disruption and weaker capital spending. Order timing may slip as companies reassess risk."},
                {"sector_name": "Gold", "direction": "rise", "confidence": 67, "reasoning": "Crisis periods can increase safe-haven demand. Gold often benefits when investors hedge geopolitical or inflation risk."},
            ],
        }

    def _demo_chat(self, message: str, context: str) -> str:
        if not context.strip():
            return "I do not have matching crisis data yet. Try fetching news first or broaden the search."
        return (
            "Based on the stored crisis analysis, the strongest signals are in sectors repeatedly tied to supply, inflation, "
            "or safety trades. Energy-related shocks tend to support Oil & Gas while pressuring Airlines and Transport, "
            "and macro uncertainty tends to favor defensive sectors or Gold. The confidence levels in the dashboard show how strong each stored signal is."
        )
