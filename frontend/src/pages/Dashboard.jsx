import { RefreshCw } from "lucide-react";
import { useMemo, useState } from "react";

import { api } from "../api.js";
import EventCard from "../components/EventCard.jsx";
import SectorCard from "../components/SectorCard.jsx";
import TrendChart from "../components/TrendChart.jsx";
import { useAsync } from "../hooks.js";

const categories = ["", "Geopolitical", "Economic", "Natural Disaster", "Energy", "Health"];

export default function Dashboard() {
  const [category, setCategory] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);
  const events = useAsync(() => api.events({ category, limit: 12 }), [category, refreshKey]);
  const summary = useAsync(() => api.predictionSummary(), [refreshKey]);
  const predictions = useAsync(() => api.predictions({ limit: 100 }), [refreshKey]);
  const sectors = summary.data?.sectors || [];
  const totalPredictions = useMemo(() => sectors.reduce((sum, item) => sum + item.prediction_count, 0), [sectors]);

  async function fetchNews() {
    await api.fetchEvents();
    setRefreshKey((key) => key + 1);
  }

  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <span className="eyebrow">Global crisis monitor</span>
          <h1>Market impact dashboard</h1>
          <p>Live crisis events, AI summaries, and sector-level predictions in one operating view.</p>
        </div>
        <button className="primary-button" onClick={fetchNews}>
          <RefreshCw size={17} aria-hidden="true" />
          Fetch news
        </button>
      </header>

      <section className="metric-grid" aria-label="Dashboard metrics">
        <Metric label="Tracked events" value={events.data?.length || 0} />
        <Metric label="Sector signals" value={totalPredictions} />
        <Metric label="High severity" value={(events.data || []).filter((event) => event.severity === "High").length} />
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <h2>Sector Impact</h2>
            <p>Aggregated AI predictions ranked by confidence.</p>
          </div>
        </div>
        <div className="sector-grid">
          {sectors.map((sector) => (
            <SectorCard key={sector.sector_name} sector={sector} />
          ))}
        </div>
      </section>

      <section className="section-block">
        <div className="section-heading">
          <div>
            <h2>7-Day Prediction Trend</h2>
            <p>Average confidence from stored sector predictions.</p>
          </div>
        </div>
        <TrendChart predictions={predictions.data || []} />
      </section>

      <section className="section-block">
        <div className="section-heading feed-heading">
          <div>
            <h2>Live Crisis Feed</h2>
            <p>Filter by event type or open a full AI analysis.</p>
          </div>
          <select value={category} onChange={(event) => setCategory(event.target.value)} aria-label="Filter by category">
            {categories.map((item) => (
              <option key={item || "all"} value={item}>
                {item || "All categories"}
              </option>
            ))}
          </select>
        </div>
        {events.loading ? <div className="empty-state">Loading events...</div> : null}
        {events.error ? <div className="empty-state">Unable to load events.</div> : null}
        <div className="event-grid">
          {(events.data || []).map((event) => (
            <EventCard key={event.id} event={event} />
          ))}
        </div>
      </section>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric-tile">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

