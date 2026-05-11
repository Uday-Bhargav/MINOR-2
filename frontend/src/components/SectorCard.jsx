import { ArrowDown, ArrowRight, ArrowUp } from "lucide-react";

export default function SectorCard({ sector }) {
  const direction = sector.direction || "neutral";
  const Icon = direction === "rise" ? ArrowUp : direction === "fall" ? ArrowDown : ArrowRight;
  return (
    <article className={`sector-card ${direction}`}>
      <div className="sector-icon">
        <Icon size={18} aria-hidden="true" />
      </div>
      <div>
        <h3>{sector.sector_name}</h3>
        <p>{directionLabel(direction)}</p>
      </div>
      <strong>{sector.confidence}%</strong>
    </article>
  );
}

function directionLabel(direction) {
  if (direction === "rise") return "Expected rise";
  if (direction === "fall") return "Expected fall";
  return "Neutral signal";
}

