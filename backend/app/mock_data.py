from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.models import Category, CrisisEvent, Direction, SectorPrediction, Severity


def build_demo_events() -> list[CrisisEvent]:
    now = datetime.now(timezone.utc)
    seed = [
        (
            "Red Sea shipping disruption raises insurance costs",
            "Red Sea Disruption",
            "Red Sea",
            Category.geopolitical,
            Severity.high,
            "Attacks near key shipping routes are forcing carriers to reroute vessels. Energy and logistics markets face higher costs while airlines may see margin pressure from fuel volatility. The event is likely to keep risk premiums elevated until safe passage improves.",
            [
                ("Oil & Gas", Direction.rise, 82, "Supply routes are exposed to higher freight and insurance costs, which can lift crude and refined product prices."),
                ("Airlines", Direction.fall, 74, "Higher fuel costs and geopolitical uncertainty usually pressure airline margins."),
                ("Shipping", Direction.rise, 68, "Container rates can rise when rerouting reduces available capacity and lengthens voyages."),
            ],
        ),
        (
            "Central bank signals slower rate cuts after inflation surprise",
            "Inflation Repricing",
            "United States",
            Category.economic,
            Severity.medium,
            "A fresh inflation surprise has pushed policymakers toward a more cautious rate-cut path. Rate-sensitive sectors may underperform while banks can benefit from higher-for-longer yields. Investors are likely to rotate toward cash-flow resilient companies.",
            [
                ("Banks", Direction.rise, 71, "Higher yields can support net interest margins if credit losses remain contained."),
                ("Real Estate", Direction.fall, 79, "Property valuations are sensitive to discount rates and refinancing costs."),
                ("Technology", Direction.fall, 62, "Long-duration growth stocks often struggle when expected rates move higher."),
            ],
        ),
        (
            "Major storm threatens Gulf Coast energy infrastructure",
            "Gulf Storm",
            "Gulf of Mexico",
            Category.natural_disaster,
            Severity.high,
            "A major storm is threatening offshore platforms and refinery operations along the Gulf Coast. Temporary shutdowns could tighten fuel supply and disrupt chemical production. Market impact depends on damage assessments and restart timelines.",
            [
                ("Oil & Gas", Direction.rise, 76, "Production shut-ins can reduce near-term supply and lift prices."),
                ("Chemicals", Direction.fall, 65, "Feedstock and plant disruptions can pressure production volumes."),
                ("Insurance", Direction.fall, 58, "Large insured losses can weigh on property and casualty carriers."),
            ],
        ),
    ]

    events: list[CrisisEvent] = []
    for index, (title, event_name, location, category, severity, summary, predictions) in enumerate(seed):
        event_id = uuid4()
        event = CrisisEvent(
            id=event_id,
            title=title,
            event_name=event_name,
            location=location,
            category=category,
            severity=severity,
            summary=summary,
            source_url=f"https://example.com/crisis/{index + 1}",
            published_at=now - timedelta(days=index + 1, hours=index * 3),
        )
        event.predictions = [
            SectorPrediction(
                event_id=event_id,
                sector_name=sector,
                direction=direction,
                confidence=confidence,
                reasoning=reasoning,
                created_at=event.created_at,
            )
            for sector, direction, confidence, reasoning in predictions
        ]
        events.append(event)
    return events

