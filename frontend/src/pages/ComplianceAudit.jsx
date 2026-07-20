import { useEffect, useState } from "react";
import StatusBadge from "../components/ui/StatusBadge";
import { compliance, getApiErrorMessage } from "../services/api";

export default function ComplianceAudit() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  useEffect(() => { compliance("OISD-118").then(setData).catch((requestError) => setError(getApiErrorMessage(requestError))); }, []);
  return <div className="space-y-6">
    <div className="flex flex-wrap items-start justify-between gap-3"><div><h1 className="text-2xl font-semibold">Compliance Audit</h1><p className="text-sm text-text-secondary">Prototype evidence-gap assessment derived from inspection records.</p></div><span className="rounded-full border border-warning/40 px-3 py-1 text-xs text-warning">Synthetic demo data</span></div>
    {error && <div className="rounded-xl border border-critical/40 bg-critical/10 p-4 text-sm text-critical">{error}</div>}
    {!data && !error && <p className="text-sm text-text-secondary">Evaluating inspection evidence…</p>}
    {data && <>
      <div className="grid gap-4 sm:grid-cols-4"><Metric label="Requirements checked" value={data.requirements_checked} /><Metric label="Evidence gaps" value={data.summary.gaps} className="text-warning" /><Metric label="Critical gaps" value={data.summary.critical} className="text-critical" /><Metric label="Compliant" value={`${data.compliance_percentage}%`} className="text-success" /></div>
      <div className="rounded-xl border border-warning/30 bg-warning/10 p-4 text-xs text-warning">{data.disclaimer}</div>
      <section className="overflow-hidden rounded-xl border border-border bg-surface"><div className="border-b border-border p-5"><h2 className="font-semibold">{data.standard} evidence matrix</h2><p className="text-xs text-text-secondary">Evidence confidence {Math.round(data.confidence * 100)}%</p></div><div className="overflow-x-auto"><table className="w-full min-w-[820px] text-left text-sm"><thead className="bg-card text-xs uppercase text-muted"><tr><th className="p-4">Clause</th><th>Requirement</th><th>Source evidence</th><th>Severity</th><th>Status</th></tr></thead><tbody>{data.matrix.map((row) => <tr className="border-t border-border" key={row.clause}><td className="p-4 font-mono text-primary">{row.clause}</td><td>{row.requirement}</td><td className="max-w-xs text-text-secondary">{row.evidence_source}</td><td>{row.severity}</td><td><StatusBadge tone={row.status === "CRITICAL" ? "red" : row.status === "GAP" ? "amber" : "green"}>{row.status}</StatusBadge></td></tr>)}</tbody></table></div></section>
      <section className="rounded-xl border border-border bg-surface p-5"><h2 className="font-semibold">Ranked corrective actions</h2><ol className="mt-4 space-y-3">{data.corrective_actions.map((action) => <li key={action.clause} className="rounded-lg bg-card p-4 text-sm"><span className="mr-3 font-mono text-primary">#{action.rank}</span><strong>{action.clause}</strong><span className="ml-3 text-text-secondary">{action.remediation}</span></li>)}</ol></section>
    </>}
  </div>;
}

function Metric({ label, value, className = "" }) { return <div className="rounded-xl border border-border bg-surface p-5"><p className="text-xs text-muted">{label}</p><p className={`mt-2 text-3xl ${className}`}>{value}</p></div>; }
