import { useEffect, useState } from "react";

import LoadingState from "../components/ui/LoadingState";
import StatusBadge from "../components/ui/StatusBadge";
import { compliance, getApiErrorMessage } from "../services/api";

export default function ComplianceAudit() {
  const [data, setData] = useState(null); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  useEffect(() => { let ignore=false; compliance("OISD-118").then((result)=>{if(!ignore)setData(result)}).catch((requestError)=>{if(!ignore)setError(getApiErrorMessage(requestError))}).finally(()=>{if(!ignore)setLoading(false)}); return()=>{ignore=true}; },[]);
  return <div className="space-y-6">
    <div><h1 className="text-2xl font-semibold">Compliance Audit</h1><p className="text-sm text-text-secondary">Prototype evidence-gap assessment against synthetic OISD-118 inspection records. Not legal certification.</p></div>
    {loading&&<LoadingState message="Mapping OISD-118 evidence..."/>}{!loading&&error&&<p className="rounded-lg border border-critical/30 bg-critical/5 p-4 text-sm text-critical">{error}</p>}
    {!loading&&data?.status==="no_data"&&<p className="rounded-lg border border-warning/30 bg-warning/5 p-4 text-sm text-warning">{data.message}</p>}
    {!loading&&data?.status==="ok"&&<>
      <div className="grid gap-4 sm:grid-cols-4"><div className="rounded-xl border border-border bg-surface p-5"><p className="text-xs text-muted">Compliance evidence</p><p className="mt-2 text-3xl">{data.compliance_percentage}%</p></div><div className="rounded-xl border border-border bg-surface p-5"><p className="text-xs text-muted">Checked</p><p className="mt-2 text-3xl">{data.requirements_checked}</p></div><div className="rounded-xl border border-warning/30 bg-surface p-5"><p className="text-xs text-muted">Gaps</p><p className="mt-2 text-3xl text-warning">{data.summary.gaps}</p></div><div className="rounded-xl border border-critical/30 bg-surface p-5"><p className="text-xs text-muted">Critical</p><p className="mt-2 text-3xl text-critical">{data.summary.critical}</p></div></div>
      <section className="overflow-hidden rounded-xl border border-border bg-surface"><div className="border-b border-border p-5"><h2 className="font-semibold">OISD-118 evidence matrix</h2><p className="text-xs text-text-secondary">Analysis {data.metadata.analysis_id} · records and counts returned by the API</p></div><div className="overflow-x-auto"><table className="w-full min-w-[760px] text-left text-sm"><thead className="bg-card text-xs uppercase text-muted"><tr><th className="p-4">Record / clause</th><th>Requirement</th><th>Evidence</th><th>Status</th><th>Remediation</th></tr></thead><tbody>{data.matrix.map((row)=><tr className="border-t border-border" key={row.record_id}><td className="p-4 font-mono text-primary">{row.record_id}<br/><span className="text-muted">{row.clause}</span></td><td>{row.requirement}</td><td className="text-text-secondary">{row.evidence_source}</td><td><StatusBadge tone={row.status==="CRITICAL"?"red":row.status==="GAP"?"amber":"green"}>{row.status}</StatusBadge></td><td className="pr-4 text-text-secondary">{row.remediation}</td></tr>)}</tbody></table></div></section>
      <section className="rounded-xl border border-border bg-surface p-5"><h2 className="font-semibold">Prioritised corrective actions</h2><ol className="mt-4 space-y-3">{data.corrective_actions.map((action)=><li className="rounded-lg bg-card p-4 text-sm" key={action.record_id}><span className="mr-3 font-mono text-primary">#{action.rank}</span>{action.remediation}<span className="ml-2 text-xs text-muted">({action.record_id})</span></li>)}</ol></section>
    </>}
  </div>;
}
