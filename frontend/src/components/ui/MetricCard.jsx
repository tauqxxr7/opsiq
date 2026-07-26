export default function MetricCard({ label, value, detail, icon: Icon, tone = "text-primary" }) {
  return (
    <article className="card-hover group rounded-xl border border-border bg-surface p-5 shadow-panel">
      <div className="mb-3 flex items-center justify-between gap-3">
        <p className="text-xs font-medium uppercase tracking-widest text-muted">{label}</p>
        {Icon && <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-primary/20 bg-primary/10"><Icon className={tone} size={16} aria-hidden="true" /></div>}
      </div>
      <p className={`metric-value mb-1 font-mono text-3xl font-bold tabular-nums ${tone}`}>{value}</p>
      <p className="text-xs leading-relaxed text-text-secondary">{detail}</p>
    </article>
  );
}