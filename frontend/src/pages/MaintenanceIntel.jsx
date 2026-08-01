import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import HealthTimeline from "../components/charts/HealthTimeline";
import LoadingState from "../components/ui/LoadingState";
import PageHeader from "../components/ui/PageHeader";
import Panel from "../components/ui/Panel";
import StatusBadge from "../components/ui/StatusBadge";
import { ErrorState, EmptyState } from "../components/ui/StatePanel";
import { generateWorkOrder, getApiErrorMessage, maintenance, maintenanceCatalog } from "../services/api";

const equipmentGroups = [
  ["Pumps", "P-"],
  ["Vessels", "V-"],
  ["Compressors", "C-"],
];

const riskTone = (level) => level === "CRITICAL" ? "red" : level === "HIGH" ? "amber" : level === "MONITOR" ? "blue" : "green";

export default function MaintenanceIntel() {
  const [params] = useSearchParams();
  const [activeTab, setActiveTab] = useState("analysis");
  const [id, setId] = useState(params.get("equipment") || "P-201");
  const [equipmentIds, setEquipmentIds] = useState(["P-201"]);
  const [registry, setRegistry] = useState([]);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [reload, setReload] = useState(0);
  const [workOrder, setWorkOrder] = useState(null);
  const [drafting, setDrafting] = useState(false);
  const [approvalNote, setApprovalNote] = useState("");

  useEffect(() => {
    let ignore = false;
    maintenanceCatalog().then((result) => {
      if (!ignore && result.equipment?.length) {
        setRegistry(result.equipment);
        setEquipmentIds(result.equipment.map((item) => item.equipment_id));
      }
    }).catch(() => {});
    return () => { ignore = true; };
  }, []);

  useEffect(() => {
    let ignore = false;
    setLoading(true);
    setError("");
    maintenance(id).then((result) => {
      if (!ignore) setData(result);
    }).catch((requestError) => {
      if (!ignore) {
        setData(null);
        setError(getApiErrorMessage(requestError));
      }
    }).finally(() => {
      if (!ignore) setLoading(false);
    });
    return () => { ignore = true; };
  }, [id, reload]);

  const highlightedEquipment = useMemo(
    () => new Set([...registry].sort((left, right) => right.risk_score - left.risk_score).slice(0, 5).map((item) => item.equipment_id)),
    [registry],
  );

  const draftWorkOrder = async () => {
    setDrafting(true); setApprovalNote("");
    try { setWorkOrder(await generateWorkOrder(id)); } catch (requestError) { setError(getApiErrorMessage(requestError)); } finally { setDrafting(false); }
  };

  const downloadDraft = () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(workOrder, null, 2)], { type: "text/plain" }));
    const link = document.createElement("a"); link.href = url; link.download = `${workOrder.work_order_id}.txt`; link.click(); URL.revokeObjectURL(url);
  };
  const selectEquipment = (equipmentId) => {
    setId(equipmentId);
    setActiveTab("analysis");
  };

  return <div className="page-enter page-enter-active space-y-6">
    <PageHeader eyebrow="Reliability intelligence" title="Maintenance intelligence" description="Historical recurrence-risk scoring from synthetic work-order evidence. This analysis does not predict a future failure date." actions={activeTab === "analysis" ? <label className="block text-xs font-medium text-text-secondary">Equipment<select aria-label="Equipment ID" value={id} onChange={(event) => setId(event.target.value)} className="ml-2 rounded-md border border-border bg-surface px-3 py-2 text-sm text-text-primary">{equipmentIds.map((equipmentId) => <option key={equipmentId}>{equipmentId}</option>)}</select></label> : null} />
    <div className="flex gap-1 rounded-xl border border-border bg-surface p-1" role="tablist" aria-label="Maintenance views">
      <button type="button" role="tab" aria-selected={activeTab === "analysis"} onClick={() => setActiveTab("analysis")} className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${activeTab === "analysis" ? "bg-primary/15 text-primary" : "text-text-secondary hover:bg-card hover:text-text-primary"}`}>Risk analysis</button>
      <button type="button" role="tab" aria-selected={activeTab === "registry"} onClick={() => setActiveTab("registry")} className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors ${activeTab === "registry" ? "bg-primary/15 text-primary" : "text-text-secondary hover:bg-card hover:text-text-primary"}`}>Equipment Registry</button>
    </div>

    {activeTab === "registry" ? <Panel title="Equipment registry" description="Synthetic equipment hierarchy grouped by industrial asset type. The five highest-risk assets expose their current score immediately.">
      <div className="space-y-6">
        {equipmentGroups.map(([groupName, prefix]) => {
          const items = registry.filter((item) => item.equipment_id.startsWith(prefix));
          return <section key={prefix}>
            <div className="mb-3 flex items-center justify-between"><h2 className="text-xs font-semibold uppercase tracking-widest text-muted">{groupName}</h2><span className="font-mono text-xs text-muted">{items.length}</span></div>
            {items.length ? <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">{items.map((item) => {
              const highlighted = highlightedEquipment.has(item.equipment_id);
              const lastFailure = item.evidence?.reduce((latest, record) => record.date > latest ? record.date : latest, "") || "No dated record";
              return <button type="button" key={item.equipment_id} onClick={() => selectEquipment(item.equipment_id)} className="card-hover rounded-xl border border-border bg-card/40 p-4 text-left">
                <div className="flex items-start justify-between gap-3"><span className="font-mono text-sm font-semibold text-primary">{item.equipment_id}</span>{highlighted ? <StatusBadge tone={riskTone(item.risk_level)}>{item.risk_level}</StatusBadge> : <span className="text-xs text-muted">Click to analyze</span>}</div>
                <dl className="mt-4 grid grid-cols-2 gap-3 text-xs"><div><dt className="text-muted">Last failure</dt><dd className="mt-1 font-mono text-text-primary">{lastFailure}</dd></div><div><dt className="text-muted">Incidents</dt><dd className="mt-1 font-mono text-text-primary">{item.evidence?.length ?? 0}</dd></div></dl>
              </button>;
            })}</div> : <EmptyState title={`No ${groupName.toLowerCase()} in dataset`} description={`No ${prefix}series equipment records are present in the current synthetic evidence.`} />}
          </section>;
        })}
      </div>
    </Panel> : <>
      {loading && <Panel><LoadingState message="Analysing work-order evidence..." /></Panel>}
      {!loading && error && <ErrorState message={error} onRetry={() => setReload((value) => value + 1)} />}
      {!loading && data?.status === "no_data" && <Panel><EmptyState title="No equipment evidence" description={data.message} /></Panel>}
      {!loading && data?.status === "ok" && <>
        <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
          <Panel title="Recurrence risk" description="Six-component deterministic score.">
            <div className="risk-score"><div className="mb-2 flex items-baseline gap-2"><span className="metric-value font-mono text-5xl font-bold text-text-primary">{data.risk_score}</span><span className="font-mono text-lg text-muted">/ 100</span></div><div className="mb-3 h-2 overflow-hidden rounded-full bg-border"><div className={`h-full rounded-full transition-all duration-700 ${data.risk_level === "CRITICAL" ? "bg-critical" : "bg-warning"}`} style={{ width: `${data.risk_score}%` }} /></div><StatusBadge tone={data.risk_level === "CRITICAL" ? "red" : "amber"}>{data.risk_level}</StatusBadge></div>
            <p className="mt-5 text-xs text-text-secondary">{data.evidence.length} work orders / {Math.round(data.confidence * 100)}% evidence confidence</p>
          </Panel>
          <Panel title="Observed failure intervals" description="Days between dated records; no future date is inferred."><HealthTimeline intervals={data.recurrence.interval_days} /></Panel>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {[["Dominant failure mode", data.dominant_failure_mode], ["Dominant root cause", data.dominant_root_cause], ["Analysis identity", data.metadata.analysis_id ?? data.metadata.dataset_hash.slice(0, 12)]].map(([label, value]) => <div key={label} className="card-hover rounded-xl border border-border bg-surface p-5 shadow-panel"><p className="text-xs text-muted">{label}</p><p className="mt-1 break-words text-sm font-medium">{value}</p></div>)}
        </div>
        <Panel title="Maintenance work order" description="Generate an evidence-informed draft for engineer review." action={<button type="button" onClick={draftWorkOrder} disabled={drafting} className="rounded-lg bg-primary px-4 py-2 text-xs font-semibold text-white disabled:opacity-60">{drafting ? "Drafting work order..." : "Generate work order"}</button>}>
          {workOrder ? <div className="space-y-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="font-mono text-sm font-semibold text-primary">{workOrder.work_order_id}</p><p className="mt-1 text-xs text-text-secondary">Priority: {workOrder.priority} · Due {new Date(workOrder.due_by).toLocaleString()}</p></div><StatusBadge tone={riskTone(workOrder.priority)}>{workOrder.status}</StatusBadge></div>
            <div className="grid gap-5 md:grid-cols-2"><section><h3 className="text-xs font-semibold uppercase tracking-widest text-muted">Recommended actions</h3><ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-text-secondary">{workOrder.recommended_actions.map((item) => <li key={item}>{item}</li>)}</ul></section><section><h3 className="text-xs font-semibold uppercase tracking-widest text-warning">Safety precautions</h3><ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-text-secondary">{workOrder.safety_precautions.map((item) => <li key={item}>{item}</li>)}</ul></section></div>
            <dl className="grid gap-3 text-xs sm:grid-cols-3"><div><dt className="text-muted">Required skills</dt><dd className="mt-1">{workOrder.required_skills.join(", ")}</dd></div><div><dt className="text-muted">Required parts</dt><dd className="mt-1">{workOrder.required_parts.join(", ")}</dd></div><div><dt className="text-muted">Estimated duration</dt><dd className="mt-1 font-mono">{workOrder.estimated_duration_hours} hours</dd></div></dl>
            <div className="flex flex-wrap gap-3"><button type="button" onClick={downloadDraft} className="rounded-lg border border-border bg-card px-4 py-2 text-xs font-semibold">Download draft</button><button type="button" onClick={() => setApprovalNote("In production, this would notify the assigned supervisor. Demo mode active.")} className="rounded-lg border border-primary/30 bg-primary/10 px-4 py-2 text-xs font-semibold text-primary">Request approval</button></div>{approvalNote && <p role="status" className="text-xs text-warning">{approvalNote}</p>}
          </div> : <p className="text-sm text-text-secondary">No draft generated. Review the risk evidence before creating a work order.</p>}
        </Panel>        <Panel title="Score breakdown" description={`Dataset ${data.metadata.dataset_hash.slice(0, 12)}... / ${data.metadata.methodology_version}`} flush>
          <div className="overflow-x-auto"><table className="data-table w-full min-w-[720px]"><thead className="bg-card"><tr><th>Component</th><th>Score</th><th>Weight</th><th>Evidence</th></tr></thead><tbody>{Object.entries(data.risk_breakdown).map(([name, item]) => <tr className="evidence-row" key={name}><td className="font-medium capitalize">{name.replaceAll("_", " ")}</td><td className="font-mono">{item.score}</td><td className="font-mono">{item.weight}</td><td className="max-w-xl break-words font-mono text-xs text-text-secondary">{JSON.stringify(item.evidence)}</td></tr>)}</tbody></table></div>
        </Panel>
        <Panel title="Supporting work-order evidence" description="Dated records used by this analysis." flush>
          <div className="overflow-x-auto"><table className="data-table w-full min-w-[760px]"><thead className="bg-card"><tr><th>Work order</th><th>Date</th><th>Failure type</th><th>Severity</th><th>Downtime</th></tr></thead><tbody>{data.evidence.map((record) => <tr className="evidence-row" key={record.record_id}><td className="font-mono font-medium text-primary">{record.record_id}</td><td className="font-mono">{record.date}</td><td>{record.failure_type}</td><td>{record.severity}</td><td className="font-mono">{record.downtime_hours} h</td></tr>)}</tbody></table></div>
        </Panel>
        <div className="border-l-2 border-muted bg-card px-4 py-3 text-xs leading-5 text-text-secondary"><strong className="text-text-primary">Methodology:</strong> {data.methodology.name}. The score summarizes historical recurrence evidence and must not be interpreted as a predicted failure window.</div>
      </>}
    </>}
  </div>;
}
