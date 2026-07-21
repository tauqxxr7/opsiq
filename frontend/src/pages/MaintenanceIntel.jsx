import { useEffect, useState } from "react";
import HealthTimeline from "../components/charts/HealthTimeline";
import LoadingState from "../components/ui/LoadingState";
import PageHeader from "../components/ui/PageHeader";
import Panel from "../components/ui/Panel";
import StatusBadge from "../components/ui/StatusBadge";
import { ErrorState, EmptyState } from "../components/ui/StatePanel";
import { getApiErrorMessage, maintenance, maintenanceCatalog } from "../services/api";

export default function MaintenanceIntel() {
  const [id, setId] = useState("P-201");
  const [equipmentIds, setEquipmentIds] = useState(["P-201"]);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);

  useEffect(() => { let ignore = false; maintenanceCatalog().then((result) => { if (!ignore && result.equipment?.length) setEquipmentIds(result.equipment.map((item) => item.equipment_id)); }).catch(() => {}); return () => { ignore = true; }; }, []);
  useEffect(() => {
    let ignore = false; setLoading(true); setError("");
    maintenance(id).then((result) => { if (!ignore) setData(result); }).catch((requestError) => { if (!ignore) { setData(null); setError(getApiErrorMessage(requestError)); } }).finally(() => { if (!ignore) setLoading(false); });
    return () => { ignore = true; };
  }, [id, reload]);

  return <div className="space-y-6">
    <PageHeader eyebrow="Reliability intelligence" title="Maintenance intelligence" description="Historical recurrence-risk scoring from synthetic work-order evidence. This analysis does not predict a future failure date." actions={<label className="block text-xs font-medium text-text-secondary">Equipment<select aria-label="Equipment ID" value={id} onChange={(event) => setId(event.target.value)} className="ml-2 rounded-md border border-border bg-surface px-3 py-2 text-sm text-text-primary">{equipmentIds.map((equipmentId) => <option key={equipmentId}>{equipmentId}</option>)}</select></label>} />
    {loading && <Panel><LoadingState message="Analysing work-order evidence..." /></Panel>}
    {!loading && error && <ErrorState message={error} onRetry={() => setReload((value) => value + 1)} />}
    {!loading && data?.status === "no_data" && <Panel><EmptyState title="No equipment evidence" description={data.message} /></Panel>}
    {!loading && data?.status === "ok" && <>
      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <Panel title="Recurrence risk" description="Six-component deterministic score.">
          <div className="flex items-end justify-between"><p className="text-4xl font-semibold tabular-nums">{data.risk_score}<span className="text-sm font-normal text-muted"> / 100</span></p><StatusBadge tone={data.risk_level === "CRITICAL" ? "red" : "amber"}>{data.risk_level}</StatusBadge></div>
          <p className="mt-5 text-xs text-text-secondary">{data.evidence.length} work orders  /  {Math.round(data.confidence * 100)}% evidence confidence</p>
        </Panel>
        <Panel title="Observed failure intervals" description="Days between dated records; no future date is inferred."><HealthTimeline intervals={data.recurrence.interval_days} /></Panel>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        {[["Dominant failure mode", data.dominant_failure_mode], ["Dominant root cause", data.dominant_root_cause], ["Analysis identity", data.metadata.analysis_id ?? data.metadata.dataset_hash.slice(0, 12)]].map(([label, value]) => <div key={label} className="border-l-2 border-primary bg-surface px-4 py-3 shadow-panel"><p className="text-xs text-muted">{label}</p><p className="mt-1 break-words text-sm font-medium">{value}</p></div>)}
      </div>
      <Panel title="Score breakdown" description={`Dataset ${data.metadata.dataset_hash.slice(0, 12)}...  /  ${data.metadata.methodology_version}`} flush>
        <div className="overflow-x-auto"><table className="data-table w-full min-w-[720px]"><thead className="bg-card"><tr><th>Component</th><th>Score</th><th>Weight</th><th>Evidence</th></tr></thead><tbody>{Object.entries(data.risk_breakdown).map(([name, item]) => <tr key={name}><td className="font-medium capitalize">{name.replaceAll("_", " ")}</td><td className="font-mono">{item.score}</td><td className="font-mono">{item.weight}</td><td className="max-w-xl break-words font-mono text-xs text-text-secondary">{JSON.stringify(item.evidence)}</td></tr>)}</tbody></table></div>
      </Panel>
      <Panel title="Supporting work-order evidence" description="Dated records used by this analysis." flush>
        <div className="overflow-x-auto"><table className="data-table w-full min-w-[760px]"><thead className="bg-card"><tr><th>Work order</th><th>Date</th><th>Failure type</th><th>Severity</th><th>Downtime</th></tr></thead><tbody>{data.evidence.map((record) => <tr key={record.record_id}><td className="font-mono font-medium text-primary">{record.record_id}</td><td>{record.date}</td><td>{record.failure_type}</td><td>{record.severity}</td><td>{record.downtime_hours} h</td></tr>)}</tbody></table></div>
      </Panel>
      <div className="border-l-2 border-muted bg-card px-4 py-3 text-xs leading-5 text-text-secondary"><strong className="text-text-primary">Methodology:</strong> {data.methodology.name}. The score summarizes historical recurrence evidence and must not be interpreted as a predicted failure window.</div>
    </>}
  </div>;
}