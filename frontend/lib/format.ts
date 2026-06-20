export function label(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function percent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function scoreTone(score: number) {
  if (score >= 90) return "excellent";
  if (score >= 75) return "good";
  if (score >= 60) return "review";
  return "risk";
}

