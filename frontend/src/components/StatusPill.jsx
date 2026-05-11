export default function StatusPill({ value, tone }) {
  return <span className={`pill ${tone || value?.toLowerCase?.().replace(/\s+/g, "-")}`}>{value}</span>;
}

