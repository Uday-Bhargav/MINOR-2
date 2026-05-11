export function formatDate(value) {
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function directionSymbol(direction) {
  if (direction === "rise") return "Up";
  if (direction === "fall") return "Down";
  return "Flat";
}

