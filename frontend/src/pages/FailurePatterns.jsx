import { useEffect, useState } from "react";
import { getApiErrorMessage, patterns } from "../services/api";

export default function FailurePatterns() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { patterns().then(setData).catch((requestError) => setError(getApiErrorMessage(requestError))); }, []);
  return <div className="space-y-6">
    <div className="flex flex-wrap items-start justify-between gap-3"><div><h1 className="text-2xl font-semibold">Failure Pattern Engine</h1><p className="text-sm text-text-secondary">Recurring relationships derived across work orders and incident history.</p></div><span className="rounded-full border border-warning/40 px-3 py-1 text-xs text-warning">Synthetic demo data</span></div>
    {error && <div className="rounded-xl border border-critical/40 bg-critical/10 p-4 text-sm text-critical">{error}</div>}
    {!data && !error && <p className="text-sm text-text-secondary">Aggregating cross-source evidence…</p>}
    {data && <>
      <div className="grid gap-4 sm:grid-cols-4"><Metric label="Records analyzed" value={data.records_analyzed} /><Metric label="Work orders" value={data.source_counts.work_order || 0} /><Metric label="Incident records" value={data.source_counts.incident_history || 0} /><Metric label="Graph edges" value={data.knowledge_graph.metrics.edge_count} /></div>
      <section><h2 className="mb-4 font-semibold">Recurring equipment failures</h2><div className="grid gap-5 lg:grid-cols-2">{data.patterns.map((item) => <article className="rounded-xl border border-border bg-surface p-5" key={`${item.equipment_id}-${item.failure_type}`}><div className="flex justify-between gap-3"><div><p className="font-mono text-primary">{item.equipment_id}</p><h3 className="mt-2 font-semibold">{item.failure_type}</h3></div><span className={item.risk === "CRITICAL" ? "text-xs text-critical" : "text-xs text-warning"}>{item.risk}</span></div><p className="mt-4 text-sm text-text-secondary">{item.occurrences} events · {item.cumulative_downtime_hours} downtime hours · {item.first_seen} to {item.last_seen}</p><p className="mt-3 text-xs text-muted">Sources: {item.sources.join(", ")}</p><div className="mt-3 flex flex-wrap gap-2">{item.supporting_evidence_ids.map((id) => <span className="rounded bg-card px-2 py-1 font-mono text-xs text-primary" key={id}>{id}</span>)}</div></article>)}</div></section>
      <section className="rounded-xl border border-border bg-surface p-5"><h2 className="font-semibold">Systemic root causes</h2><div className="mt-4 space-y-3">{data.recurring_root_causes.map((item) => <div className="rounded-lg bg-card p-4" key={item.value}><p className="font-medium">{item.value}</p><p className="mt-1 text-xs text-text-secondary">{item.occurrences} records across {item.equipment_ids.join(", ")} · evidence {item.supporting_evidence_ids.join(", ")}</p></div>)}</div></section>
      <section className="rounded-xl border border-border bg-surface p-5"><h2 className="font-semibold">Repeated precursor conditions</h2><div className="mt-4 grid gap-3 md:grid-cols-2">{data.repeated_precursors.slice(0, 8).map((item) => <div className="rounded-lg bg-card p-4" key={item.value}><p className="text-sm">{item.value}</p><p className="mt-2 text-xs text-muted">{item.occurrences} supporting records · {item.equipment_ids.length} equipment</p></div>)}</div><p className="mt-4 text-xs text-muted">Evidence sufficiency: {Math.round(data.confidence * 100)}%. This is deterministic aggregation, not a trained failure prediction.</p></section>
    </>}
  </div>;
}
function Metric({ label, value }) { return <div className="rounded-xl border border-border bg-surface p-5"><p className="text-xs text-muted">{label}</p><p className="mt-2 text-3xl">{value}</p></div>; }
