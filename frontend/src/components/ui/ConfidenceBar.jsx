export default function ConfidenceBar({ score = 0 }) {
  const pct = Math.max(0, Math.min(100, Math.round(score * 100))); const color = pct >= 80 ? "bg-secondary" : pct >= 60 ? "bg-warning" : "bg-critical";
  return <div className="flex items-center gap-3 text-xs"><div className="h-1.5 flex-1 overflow-hidden rounded-full bg-border"><div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} /></div><span className="whitespace-nowrap font-mono text-text-secondary">{pct}% confidence</span></div>;
}