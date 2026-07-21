import { useEffect, useState } from "react";

import HealthTimeline from "../components/charts/HealthTimeline";
import LoadingState from "../components/ui/LoadingState";
import StatusBadge from "../components/ui/StatusBadge";
import { getApiErrorMessage, maintenance } from "../services/api";

export default function MaintenanceIntel() {
  const [id, setId] = useState("P-201");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setError("");
    maintenance(id)
      .then((result) => { if (!ignore) setData(result); })
      .catch((requestError) => { if (!ignore) { setData(null); setError(getApiErrorMessage(requestError)); } })
      .finally(() => { if (!ignore) setLoading(false); });
    return () => { ignore = true; };
  }, [id]);

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-semibold">Maintenance Intelligence</h1><p className="text-sm text-text-secondary">Deterministic risk scoring from work order evidence. No ML model — transparent weighted formula.</p></div>
      <select value={id} onChange={(event) => setId(event.target.value)} className="rounded-lg border border-border bg-surface px-4 py-3 text-sm">{Array.from({ length: 15 }, (_, index) => <option key={`P-${201 + index}`}>P-{201 + index}</option>)}</select>
      {loading && <LoadingState message="Analysing work order evidence..." />}
      {!loading && error && <p className="rounded-lg border border-critical/30 bg-critical/5 p-4 text-sm text-critical">{error}</p>}
      {!loading && !data && !error && <p className="rounded-lg border border-border bg-card p-4 text-sm text-text-secondary">Select an equipment ID above to run deterministic risk analysis from work order history.</p>}
      {!loading && data && <>
        <div className="grid gap-5 lg:grid-cols-3">
          <section className="rounded-xl border border-critical/30 bg-surface p-5"><p className="text-xs uppercase tracking-widest text-muted">Risk level</p><div className="mt-4"><StatusBadge tone={data.risk_level === "CRITICAL" ? "red" : "amber"}>{data.risk_level}</StatusBadge></div><p className="mt-5 text-3xl font-semibold">{data.failure_window}</p><p className="text-xs text-text-secondary">Estimated failure window</p></section>
          <section className="rounded-xl border border-border bg-surface p-5 lg:col-span-2"><h2 className="font-semibold">14-day health timeline</h2><div className="mt-6"><HealthTimeline /></div></section>
        </div>
        <section className="rounded-xl border border-border bg-surface p-5"><h2 className="font-semibold">Structured root-cause evidence</h2><div className="mt-5 grid gap-3 md:grid-cols-3"><div className="rounded-lg bg-card p-4"><p className="text-xs text-muted">Observed</p><p className="mt-2 text-sm">Vibration rise + bearing temperature drift</p></div><div className="rounded-lg bg-card p-4"><p className="text-xs text-muted">Likely mechanism</p><p className="mt-2 text-sm">{data.predicted_component}</p></div><div className="rounded-lg bg-card p-4"><p className="text-xs text-muted">Evidence base</p><p className="mt-2 text-sm">{data.history?.length || 0} matching work orders</p></div></div></section>
      </>}
    </div>
  );
}
