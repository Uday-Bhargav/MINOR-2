import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function TrendChart({ predictions }) {
  const data = buildData(predictions);

  return (
    <div className="chart-frame">
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data} margin={{ top: 10, right: 18, left: -18, bottom: 0 }}>
          <CartesianGrid stroke="#d8e0e8" strokeDasharray="4 4" />
          <XAxis dataKey="date" tickLine={false} axisLine={false} />
          <YAxis domain={[0, 100]} tickLine={false} axisLine={false} />
          <Tooltip />
          <Line type="monotone" dataKey="confidence" stroke="#1d4ed8" strokeWidth={3} dot={{ r: 4 }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function buildData(predictions) {
  const buckets = new Map();
  const now = new Date();
  for (let i = 6; i >= 0; i -= 1) {
    const date = new Date(now);
    date.setDate(now.getDate() - i);
    const key = date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
    buckets.set(key, []);
  }

  predictions.forEach((prediction) => {
    const key = new Date(prediction.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" });
    if (buckets.has(key)) {
      buckets.get(key).push(prediction.confidence);
    }
  });

  return Array.from(buckets.entries()).map(([date, values]) => ({
    date,
    confidence: values.length ? Math.round(values.reduce((sum, value) => sum + value, 0) / values.length) : 0,
  }));
}

