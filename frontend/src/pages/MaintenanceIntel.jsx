import { useEffect, useState } from "react";
import StatusBadge from "../components/ui/StatusBadge";
import { getApiErrorMessage, maintenance } from "../services/api";

const tone = (level) => level === "CRITICAL" ? "red" : level === "LOW" ? "green" : "amber";
const label = (value) => value.replaceAll("_", " ");

export default function MaintenanceIntel() {
  const [id, setId] = useState("P-201");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => {
    setData(null); setError("");
    maintenance(id).then(setData).catch((requestError) => setError(getApiErrorMessage(requestError)));
  }, [id]);
  return <div className="space-y-6">
    <div className="flex flex-wrap items-start justify-between gap-3"><div><h1 className="text-2xl font-semibold">Maintenance Intelligence</h1><p className="text-sm text-text-secondary">Deterministic recurrence-risk analytics from synthetic work-order evidence.</p></div><span className="rounded-full border border-warning/40 px-3 py-1 text-xs text-warning">Synthetic demo data</span></div>
    <select value={id} onChange={(event) => setId(event.target.value)} className="rounded-lg border border-border bg-surface px-4 py-3 text-sm">{Array.from({ length: 15 }, (_, index) => <option key={index}>P-{201 + index}</option>)}</select>
    {error && <div className="rounded-xl border border-critical/40 bg-critical/10 p-4 text-sm text-critical">{error}</div>}
    {!data && !error && <p className="text-sm text-text-secondary">Analyzing work-order evidence…</p>}
    {data && <>
      <div className="grid gap-4 md:grid-cols-4">
        <section className="rounded-xl border border-border bg-surface p-5"><p className="text-xs uppercase text-muted">Risk</p><div className="mt-3"><StatusBadge tone={tone(data.risk_level)}>{data.risk_level}</StatusBadge></div><p className="mt-3 text-3xl font-semibold">{data.risk_score}<span className="text-sm text-muted">/100</span></p></section>
        <section className="rounded-xl border border-border bg-surface p-5"><p className="text-xs uppercase text-muted">Failure mode</p><p className="mt-3 font-medium">{data.dominant_failure_mode}</p><p className="mt-2 text-xs text-text-secondary">{data.metrics.repeated_failure_mode_frequency} supporting events</p></section>
        <section className="rounded-xl border border-border bg-surface p-5"><p className="text-xs uppercase text-muted">Downtime</p><p className="mt-3 text-2xl">{data.metrics.cumulative_downtime_hours} h</p><p className="text-xs text-text-secondary">{data.metrics.average_downtime_hours} h average</p></section>
        <section className="rounded-xl border border-border bg-surface p-5"><p className="text-xs uppercase text-muted">Interval trend</p><p className="mt-3 font-medium">{data.metrics.trend_direction}</p><p className="text-xs text-text-secondary">MTBF {data.metrics.mean_time_between_failures_days ?? "N/A"} days</p></section>
      </div>
      <section className="rounded-xl border border-border bg-surface p-5"><h2 className="font-semibold">Risk score breakdown</h2><div className="mt-4 grid gap-4 md:grid-cols-2">{Object.entries(data.risk_breakdown).map(([name, item]) => <div key={name}><div className="mb-1 flex justify-between text-xs"><span className="capitalize text-text-secondary">{label(name)}</span><span>{item.score} / {item.weight}</span></div><div className="h-2 rounded bg-border"><div className="h-full rounded bg-primary" style={{ width: `${item.normalized * 100}%` }} /></div></div>)}</div></section>
      <section className="rounded-xl border border-border bg-surface p-5"><h2 className="font-semibold">Evidence and interpretation</h2><p className="mt-3 text-sm leading-6 text-text-secondary">{data.explanation}</p><p className="mt-3 text-sm">Signal: {data.recurrence_signal}</p><div className="mt-4 flex flex-wrap gap-2">{data.supporting_evidence_ids.map((evidence) => <span key={evidence} className="rounded bg-card px-2 py-1 font-mono text-xs text-primary">{evidence}</span>)}</div><p className="mt-4 text-xs text-muted">Evidence sufficiency: {Math.round(data.confidence * 100)}%</p></section>
    </>}
  </div>;
}
