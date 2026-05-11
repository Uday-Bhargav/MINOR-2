import { ExternalLink } from "lucide-react";
import { useParams } from "react-router-dom";

import { api } from "../api.js";
import StatusPill from "../components/StatusPill.jsx";
import { useAsync } from "../hooks.js";
import { formatDate } from "../utils.js";

export default function EventDetail() {
  const { id } = useParams();
  const { data: event, loading, error } = useAsync(() => api.event(id), [id]);

  if (loading) return <div className="empty-state">Loading analysis...</div>;
  if (error || !event) return <div className="empty-state">Event not found.</div>;

  return (
    <div className="page-stack">
      <header className="page-header detail-header">
        <div>
          <span className="eyebrow">{event.event_name}</span>
          <h1>{event.title}</h1>
          <p>{event.summary}</p>
        </div>
        <a className="secondary-button" href={event.source_url} target="_blank" rel="noreferrer">
          <ExternalLink size={17} aria-hidden="true" />
          Source
        </a>
      </header>

      <section className="detail-meta">
        <StatusPill value={event.category} />
        <StatusPill value={event.severity} />
        <span>{event.location}</span>
        <span>{formatDate(event.published_at)}</span>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <h2>Sector Predictions</h2>
            <p>Direction, confidence, and reasoning generated from the event summary.</p>
          </div>
        </div>
        <div className="prediction-list">
          {event.predictions.map((prediction) => (
            <article key={prediction.id} className={`prediction-row ${prediction.direction}`}>
              <div>
                <h3>{prediction.sector_name}</h3>
                <p>{prediction.reasoning}</p>
              </div>
              <div className="prediction-score">
                <span>{prediction.direction}</span>
                <strong>{prediction.confidence}%</strong>
              </div>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}

