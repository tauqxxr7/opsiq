import { useEffect, useState } from "react";
import { Database, GitBranch, Link2 } from "lucide-react";
import LoadingState from "../components/ui/LoadingState";
import MetricCard from "../components/ui/MetricCard";
import PageHeader from "../components/ui/PageHeader";
import Panel from "../components/ui/Panel";
import StatusBadge from "../components/ui/StatusBadge";
import { EmptyState, ErrorState } from "../components/ui/StatePanel";
import { getApiErrorMessage, patterns } from "../services/api";

export default function FailurePatterns() {
  const [data, setData] = useState(null); const [loading, setLoading] = useState(true); const [error, setError] = useState(""); const [reload, setReload] = useState(0);
  useEffect(() => { let ignore = false; setLoading(true); patterns().then((result) => { if (!ignore) setData(result); }).catch((requestError) => { if (!ignore) setError(getApiErrorMessage(requestError)); }).finally(() => { if (!ignore) setLoading(false); }); return () => { ignore = true; }; }, [reload]);
  return <div className="space-y-6">
    <PageHeader eyebrow="Cross-source correlation" title="Failure patterns" description="Deterministic associations across work orders and incident history. Correlation does not establish causality." />
    {loading && <Panel><LoadingState message="Correlating evidence records..." /></Panel>}
    {!loading && error && <ErrorState message={error} onRetry={() => setReload((value) => value + 1)} />}
    {!loading && data?.status === "no_data" && <Panel><EmptyState description={data.message} /></Panel>}
    {!loading && data?.status === "ok" && <>
      <div className="grid gap-4 sm:grid-cols-3">
        <MetricCard label="Records analysed" value={data.records_analyzed} detail="Across available evidence sources" icon={Database} />
        <MetricCard label="Graph nodes" value={data.knowledge_graph.node_count} detail={`${data.knowledge_graph.edge_count} evidence relationships`} icon={GitBranch} tone="text-secondary" />
        <MetricCard label="Patterns identified" value={data.patterns.length} detail="Recurring equipment / failure pairs" icon={Link2} tone="text-warning" />
      </div>
      <Panel title="Ranked recurring patterns" description={Object.entries(data.source_counts).map(([name, count]) => `${name}: ${count}`).join(" · ")} flush>
        <div className="overflow-x-auto"><table className="data-table w-full min-w-[900px]"><thead className="bg-card"><tr><th>Equipment</th><th>Failure mode</th><th>Risk</th><th>Observed range</th><th>Occurrences</th><th>Downtime</th><th>Evidence</th></tr></thead><tbody>{data.patterns.map((pattern) => <tr key={`${pattern.equipment_id}-${pattern.failure_type}`}><td className="font-mono font-medium text-primary">{pattern.equipment_id}</td><td className="font-medium">{pattern.failure_type}</td><td><StatusBadge tone={pattern.risk === "CRITICAL" ? "red" : "amber"}>{pattern.risk}</StatusBadge></td><td className="whitespace-nowrap text-text-secondary">{pattern.first_seen} → {pattern.last_seen}</td><td>{pattern.occurrences}</td><td>{pattern.cumulative_downtime_hours} h</td><td className="max-w-sm break-words font-mono text-xs text-muted">{pattern.supporting_evidence_ids.join(", ")}</td></tr>)}</tbody></table></div>
      </Panel>
      <Panel title="Recurring cross-asset root causes" description="Shared labels observed across multiple evidence records.">
        <div className="divide-y divide-border">{data.recurring_root_causes.map((item) => <div className="py-3 first:pt-0 last:pb-0" key={item.value}><div className="flex flex-wrap items-center justify-between gap-2"><p className="text-sm font-medium">{item.value}</p><span className="text-xs text-muted">{item.occurrences} records · {item.equipment_ids.join(", ")}</span></div><p className="mt-1 break-words font-mono text-xs text-text-secondary">Evidence: {item.supporting_evidence_ids.join(", ")}</p></div>)}</div>
      </Panel>
    </>}
  </div>;
}