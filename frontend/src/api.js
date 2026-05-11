const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed: ${response.status}`);
  }

  return response.json();
}

export const api = {
  events: (params = {}) => request(`/api/events${toQuery(params)}`),
  event: (id) => request(`/api/events/${id}`),
  fetchEvents: () => request("/api/events/fetch", { method: "POST" }),
  predictions: (params = {}) => request(`/api/predictions${toQuery(params)}`),
  predictionSummary: () => request("/api/predictions/summary"),
  search: (q) => request(`/api/search${toQuery({ q })}`),
  chat: (message) => request("/api/chat", { method: "POST", body: JSON.stringify({ message }) }),
};

function toQuery(params) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.set(key, value);
    }
  });
  const queryString = query.toString();
  return queryString ? `?${queryString}` : "";
}

