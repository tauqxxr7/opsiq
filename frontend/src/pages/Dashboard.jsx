import { Activity, Files, ShieldCheck, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";
import MetricCard from "../components/ui/MetricCard";
import PageHeader from "../components/ui/PageHeader";
import Panel from "../components/ui/Panel";
import { ErrorState } from "../components/ui/StatePanel";
import { compliance, documentStats, maintenanceCatalog, patterns } from "../services/api";

export default function Dashboard() {
  const [summary, setSummary] = useState({});
  const [unavailable, setUnavailable] = useState([]);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    let ignore = false;
    Promise.allSettled([documentStats(), maintenanceCatalog(), compliance("OISD-118"), patterns()]).then((results) => {
      if (ignore) return;
      const keys = ["documents", "maintenance", "audit", "patterns"];
      const available = {};
      const failed = [];
      results.forEach((result, index) => result.status === "fulfilled" ? available[keys[index]] = result.value : failed.push(keys[index]));
      setSummary(available);
      setUnavailable(failed);
    });
    return () => { ignore = true; };
  }, [reload]);

  const equipment = summary.maintenance?.equipment ?? [];
  const evidence = equipment.flatMap((item) => item.evidence.map((record) => ({ ...record, equipment_id: item.equipment_id }))).sort((left, right) => right.date.localeCompare(left.date)).slice(0, 5);
  const priority = [...equipment].sort((left, right) => right.risk_score - left.risk_score).slice(0, 5);

  return <div className="space-y-6">
    <PageHeader eyebrow="Decision overview" title="Operational intelligence" description="Evidence-grounded maintenance, compliance, failure-pattern, and knowledge signals from the current synthetic demonstration corpus." actions={<span className="rounded bg-primary/10 px-2.5 py-1.5 text-xs font-semibold text-primary">Synthetic evidence</span>} />
    {unavailable.length > 0 && <ErrorState message={`Unavailable sources: ${unavailable.join(", ")}. Healthy API results remain visible.`} onRetry={() => setReload((value) => value + 1)} />}
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard label="Indexed chunks" value={summary.documents?.chunks ?? "--"} detail="Searchable retrieval index" icon={Files} />
      <MetricCard label="Assets with evidence" value={summary.maintenance?.equipment_count ?? "--"} detail="Unique equipment identifiers" icon={Activity} tone="text-secondary" />
      <MetricCard label="OISD-118 evidence" value={summary.audit ? `${summary.audit.compliance_percentage}%` : "--"} detail="Prototype evidence-gap result" icon={ShieldCheck} tone="text-warning" />
      <MetricCard label="High-risk assets" value={summary.maintenance?.high_risk_count ?? "--"} detail="Deterministic high or critical score" icon={TriangleAlert} tone="text-critical" />
    </div>
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_minmax(360px,.85fr)]">
      <Panel title="Priority equipment" description="Ranked by deterministic recurrence-risk score returned by the maintenance API.">
        {priority.length ? <div className="space-y-4">{priority.map((item) => <div key={item.equipment_id} className="grid grid-cols-[70px_1fr_45px] items-center gap-3 text-sm"><span className="font-mono font-medium text-primary">{item.equipment_id}</span><div className="h-2 overflow-hidden rounded-full bg-border"><div className={`h-full rounded-full ${item.risk_score >= 75 ? "bg-critical" : "bg-warning"}`} style={{ width: `${item.risk_score}%` }} /></div><span className="text-right font-mono text-xs">{item.risk_score}</span></div>)}</div> : <p className="text-sm text-text-secondary">No maintenance evidence returned.</p>}
      </Panel>
      <Panel title="Latest evidence" description="Most recent work-order records across available assets." flush>
        <div className="divide-y divide-border">{evidence.map((record) => <div className="px-5 py-3.5" key={record.record_id}><div className="flex items-start justify-between gap-3"><p className="text-sm font-medium">{record.equipment_id}  /  {record.failure_type}</p><span className="font-mono text-[11px] text-muted">{record.date}</span></div><p className="mt-1 text-xs text-text-secondary">{record.record_id}  /  {record.severity}  /  {record.downtime_hours} h downtime</p></div>)}</div>
      </Panel>
    </div>
    {summary.patterns?.knowledge_graph && <p className="text-xs text-muted">Pattern graph currently contains {summary.patterns.knowledge_graph.node_count} evidence nodes and {summary.patterns.knowledge_graph.edge_count} relationships.</p>}
  </div>;
}