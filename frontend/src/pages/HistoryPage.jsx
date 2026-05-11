import { api } from "../api.js";
import { useAsync } from "../hooks.js";
import { formatDate } from "../utils.js";

export default function HistoryPage() {
  const { data, loading, error } = useAsync(() => api.predictions({ limit: 150 }), []);

  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <span className="eyebrow">Prediction history</span>
          <h1>Historical sector signals</h1>
          <p>Review stored AI predictions, confidence, direction, and timing.</p>
        </div>
      </header>

      {loading ? <div className="empty-state">Loading predictions...</div> : null}
      {error ? <div className="empty-state">Unable to load predictions.</div> : null}
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Sector</th>
              <th>Direction</th>
              <th>Confidence</th>
              <th>Reasoning</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {(data || []).map((prediction) => (
              <tr key={prediction.id}>
                <td>{prediction.sector_name}</td>
                <td><span className={`table-direction ${prediction.direction}`}>{prediction.direction}</span></td>
                <td>{prediction.confidence}%</td>
                <td>{prediction.reasoning}</td>
                <td>{formatDate(prediction.created_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

