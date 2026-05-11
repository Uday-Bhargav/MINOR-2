import { Link } from "react-router-dom";
import { ArrowUpRight, MapPin } from "lucide-react";

import StatusPill from "./StatusPill.jsx";
import { formatDate } from "../utils.js";

export default function EventCard({ event }) {
  return (
    <article className="event-card">
      <div className="event-card-top">
        <StatusPill value={event.category} />
        <StatusPill value={event.severity} />
      </div>
      <h3>{event.title}</h3>
      <p>{event.summary}</p>
      <div className="event-meta">
        <span>
          <MapPin size={15} aria-hidden="true" />
          {event.location}
        </span>
        <span>{formatDate(event.published_at)}</span>
      </div>
      <Link className="text-link" to={`/events/${event.id}`}>
        View analysis <ArrowUpRight size={15} aria-hidden="true" />
      </Link>
    </article>
  );
}

