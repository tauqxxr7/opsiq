import { useEffect, useState } from "react";
import LoadingState from "../components/ui/LoadingState";
import MetricCard from "../components/ui/MetricCard";
import PageHeader from "../components/ui/PageHeader";
import Panel from "../components/ui/Panel";
import StatusBadge from "../components/ui/StatusBadge";
import { EmptyState, ErrorState } from "../components/ui/StatePanel";
import { compliance, getApiErrorMessage } from "../services/api";
import { ClipboardCheck, FileCheck, ShieldAlert, TriangleAlert } from "lucide-react";

export default function ComplianceAudit() {
  const [data, setData] = useState(null); const [loading, setLoading] = useState(true); const [error, setError] = useState(""); const [reload, setReload] = useState(0);
  useEffect(() => { let ignore = false; setLoading(true); compliance("OISD-118").then((result) => { if (!ignore) setData(result); }).catch((requestError) => { if (!ignore) setError(getApiErrorMessage(requestError)); }).finally(() => { if (!ignore) setLoading(false); }); return () => { ignore = true; }; }, [reload]);
  return <div className="space-y-6">
    <PageHeader eyebrow="Evidence-gap assessment" title="Compliance audit" description="Deterministic prototype assessment against synthetic OISD-118 inspection evidence. It is not legal advice or certification." actions={<StatusBadge tone="blue">OISD-118</StatusBadge>} />
    {loading && <Panel><LoadingState message="Mapping OISD-118 evidence..." /></Panel>}
    {!loading && error && <ErrorState message={error} onRetry={() => setReload((value) => value + 1)} />}
    {!loading && data?.status === "no_data" && <Panel><EmptyState description={data.message} /></Panel>}
    {!loading && data?.status === "ok" && <>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Evidence coverage" value={`${data.compliance_percentage}%`} detail="Derived from current records" icon={FileCheck} tone="text-secondary" />
        <MetricCard label="Requirements checked" value={data.requirements_checked} detail="OISD-118 evidence matrix" icon={ClipboardCheck} />
        <MetricCard label="Evidence gaps" value={data.summary.gaps} detail="Corrective action required" icon={ShieldAlert} tone="text-warning" />
        <MetricCard label="Critical findings" value={data.summary.critical} detail="Highest-priority gaps" icon={TriangleAlert} tone="text-critical" />
      </div>
      <Panel title="OISD-118 evidence matrix" description={`Analysis ${data.metadata.analysis_id} · values returned by the compliance API`} flush>
        <div className="overflow-x-auto"><table className="data-table w-full min-w-[900px]"><thead className="bg-card"><tr><th>Record / clause</th><th>Requirement</th><th>Evidence source</th><th>Status</th><th>Remediation</th></tr></thead><tbody>{data.matrix.map((row) => <tr key={row.record_id}><td><span className="font-mono font-medium text-primary">{row.record_id}</span><br /><span className="text-xs text-muted">{row.clause}</span></td><td className="max-w-xs">{row.requirement}</td><td className="max-w-xs text-text-secondary">{row.evidence_source}</td><td><StatusBadge tone={row.status === "CRITICAL" ? "red" : row.status === "GAP" ? "amber" : "green"}>{row.status}</StatusBadge></td><td className="max-w-sm text-text-secondary">{row.remediation}</td></tr>)}</tbody></table></div>
      </Panel>
      <Panel title="Prioritised corrective actions" description="Ordered by the deterministic compliance analysis.">
        <ol className="divide-y divide-border">{data.corrective_actions.map((action) => <li className="grid gap-2 py-3 first:pt-0 last:pb-0 sm:grid-cols-[36px_1fr_auto]" key={action.record_id}><span className="font-mono text-sm font-semibold text-primary">#{action.rank}</span><p className="text-sm">{action.remediation}</p><span className="font-mono text-xs text-muted">{action.record_id}</span></li>)}</ol>
      </Panel>
    </>}
  </div>;
}