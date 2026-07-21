import { useEffect, useState } from "react";

import HealthTimeline from "../components/charts/HealthTimeline";
import LoadingState from "../components/ui/LoadingState";
import StatusBadge from "../components/ui/StatusBadge";
import { getApiErrorMessage, maintenance, maintenanceCatalog } from "../services/api";

export default function MaintenanceIntel() {
  const [id, setId] = useState("P-201");
  const [equipmentIds, setEquipmentIds] = useState(["P-201"]);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;
    maintenanceCatalog().then((result) => {
      if (!ignore && result.equipment?.length) setEquipmentIds(result.equipment.map((item) => item.equipment_id));
    }).catch(() => {});
    return () => { ignore = true; };
  }, []);

  useEffect(() => {
    let ignore = false;
    setLoading(true); setError("");
    maintenance(id).then((result) => { if (!ignore) setData(result); }).catch((requestError) => { if (!ignore) { setData(null); setError(getApiErrorMessage(requestError)); } }).finally(() => { if (!ignore) setLoading(false); });
    return () => { ignore = true; };
  }, [id]);

  const noData = data?.status === "no_data";
  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-semibold">Maintenance Intelligence</h1><p className="text-sm text-text-secondary">Deterministic recurrence-risk scoring from synthetic work-order evidence; this is not a trained failure prediction.</p></div>
      <label className="block text-xs text-muted">Equipment ID<select value={id} onChange={(event) => setId(event.target.value)} className="mt-2 block rounded-lg border border-border bg-surface px-4 py-3 text-sm">{equipmentIds.map((equipmentId) => <option key={equipmentId}>{equipmentId}</option>)}</select></label>
      {loading && <LoadingState message="Analysing work-order evidence..." />}
      {!loading && error && <p className="rounded-lg border border-critical/30 bg-critical/5 p-4 text-sm text-critical">{error}</p>}
      {!loading && noData && <p className="rounded-lg border border-warning/30 bg-warning/5 p-4 text-sm text-warning">{data.message}</p>}
      {!loading && data?.status === "ok" && <>
        <div className="grid gap-5 lg:grid-cols-3">
          <section className="rounded-xl border border-warning/30 bg-surface p-5"><p className="text-xs uppercase tracking-widest text-muted">Recurrence risk</p><div className="mt-4"><StatusBadge tone={data.risk_level === "CRITICAL" ? "red" : "amber"}>{data.risk_level}</StatusBadge></div><p className="mt-5 text-3xl font-semibold">{data.risk_score}<span className="text-sm text-muted"> / 100</span></p><p className="text-xs text-text-secondary">Six-component deterministic score</p></section>
          <section className="rounded-xl border border-border bg-surface p-5 lg:col-span-2"><h2 className="font-semibold">Observed failure intervals</h2><p className="text-xs text-text-secondary">Days between dated records; no future date is predicted.</p><div className="mt-4"><HealthTimeline intervals={data.recurrence.interval_days} /></div></section>
        </div>
        <section className="rounded-xl border border-border bg-surface p-5"><h2 className="font-semibold">Evidence-derived findings</h2><div className="mt-5 grid gap-3 md:grid-cols-3"><div className="rounded-lg bg-card p-4"><p className="text-xs text-muted">Dominant failure mode</p><p className="mt-2 text-sm">{data.dominant_failure_mode}</p></div><div className="rounded-lg bg-card p-4"><p className="text-xs text-muted">Dominant root cause</p><p className="mt-2 text-sm">{data.dominant_root_cause}</p></div><div className="rounded-lg bg-card p-4"><p className="text-xs text-muted">Evidence base</p><p className="mt-2 text-sm">{data.evidence.length} work orders · confidence {Math.round(data.confidence * 100)}%</p></div></div></section>
        <section className="overflow-hidden rounded-xl border border-border bg-surface"><div className="border-b border-border p-5"><h2 className="font-semibold">Score breakdown</h2><p className="text-xs text-text-secondary">Dataset hash {data.metadata.dataset_hash.slice(0, 12)}… · {data.metadata.methodology_version}</p></div><div className="overflow-x-auto"><table className="w-full min-w-[620px] text-left text-sm"><thead className="bg-card text-xs uppercase text-muted"><tr><th className="p-4">Component</th><th>Score</th><th>Weight</th><th>Evidence</th></tr></thead><tbody>{Object.entries(data.risk_breakdown).map(([name, item]) => <tr className="border-t border-border" key={name}><td className="p-4">{name.replaceAll("_", " ")}</td><td>{item.score}</td><td>{item.weight}</td><td className="font-mono text-xs text-text-secondary">{JSON.stringify(item.evidence)}</td></tr>)}</tbody></table></div></section>
      </>}
    </div>
  );
}
