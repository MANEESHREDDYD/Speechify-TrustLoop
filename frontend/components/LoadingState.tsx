export default function LoadingState({ label = "Loading the trust layer…" }: { label?: string }) {
  return <div className="loading-state"><span className="spinner" />{label}</div>;
}

