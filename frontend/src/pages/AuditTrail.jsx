import { Clock3, FileSearch, Route } from "lucide-react";
import MetricCard from "../components/ui/MetricCard";
import PageHeader from "../components/ui/PageHeader";
import Panel from "../components/ui/Panel";
import { EmptyState, ErrorState } from "../components/ui/StatePanel";
import useApiResource from "../hooks/useApiResource";
import { recentAudit } from "../services/api";
export default function AuditTrail() {
  const { data, loading, error, reload } = useApiResource(recentAudit, []), entries = data?.entries || [];
  return <div className="space-y-6"><PageHeader eyebrow="System assurance" title="Audit trail" description="Privacy-preserving process-local query telemetry. Prompts, payloads, identities and secrets are not stored." />{error ? <ErrorState message={error} onRetry={reload} /> : null}<div className="grid gap-4 sm:grid-cols-3"><MetricCard label="Events retained" value={loading ? "--" : data?.count ?? 0} detail="Maximum 20 process-local entries" icon={FileSearch} /><MetricCard label="Persistence" value="Memory" detail="Cleared on service restart" icon={Clock3} /><MetricCard label="Payload policy" value="Metadata" detail="No query content retained" icon={Route} /></div><Panel title="Recent query events" description="Newest first / anonymised by design" flush>{entries.length ? <div className="overflow-x-auto"><table className="data-table w-full min-w-[760px]"><thead><tr><th>Timestamp</th><th>Module</th><th>Outcome</th><th>Duration</th><th>Confidence</th><th>Citations</th><th>Language</th></tr></thead><tbody>{entries.map((item, index) => <tr key={`${item.timestamp}-${index}`}><td className="font-mono text-xs">{new Date(item.timestamp).toLocaleString()}</td><td>{item.query_type}</td><td>Completed</td><td className="font-mono">{item.response_time_ms} ms</td><td className="font-mono">{Math.round(item.confidence * 100)}%</td><td className="font-mono">{item.citations_returned}</td><td className="uppercase">{item.language}</td></tr>)}</tbody></table></div> : <EmptyState title={loading ? "Loading audit events" : "No audit events yet"} description="Use Copilot or a specialist analysis to create privacy-safe telemetry." />}</Panel></div>;
}
