import { Search } from "lucide-react";
import { useState } from "react";

import { api } from "../api.js";
import EventCard from "../components/EventCard.jsx";

export default function SearchPage() {
  const [query, setQuery] = useState("oil");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event) {
    event.preventDefault();
    setLoading(true);
    try {
      setResults(await api.search(query));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <span className="eyebrow">Search archive</span>
          <h1>Find past events and analysis</h1>
          <p>Search by keyword, sector, category, or location.</p>
        </div>
      </header>

      <form className="search-bar" onSubmit={onSubmit}>
        <Search size={19} aria-hidden="true" />
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search oil, banks, drought..." />
        <button className="primary-button" type="submit">Search</button>
      </form>

      {loading ? <div className="empty-state">Searching...</div> : null}
      <div className="event-grid">
        {results.map((event) => (
          <EventCard key={event.id} event={event} />
        ))}
      </div>
    </div>
  );
}

