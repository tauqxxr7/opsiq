import { useEffect, useState } from "react";

import LoadingState from "../components/ui/LoadingState";
import StatusBadge from "../components/ui/StatusBadge";
import { compliance, getApiErrorMessage } from "../services/api";

export default function ComplianceAudit() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;
    compliance("OISD-118")
      .then((result) => {
        if (ignore) return;
        setData(result);
        const percentage = result.compliance_percentage ?? Math.round((result.summary.compliant / result.requirements_checked) * 10_000) / 100;
        globalThis.localStorage?.setItem("opsiq:compliance-posture", String(percentage));
      })
      .catch((requestError) => { if (!ignore) setError(getApiErrorMessage(requestError)); })
      .finally(() => { if (!ignore) setLoading(false); });
    return () => { ignore = true; };
  }, []);

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-semibold">Compliance Audit</h1><p className="text-sm text-text-secondary">Evidence-gap assessment against OISD-118. Prototype only — not legal certification.</p></div>
      {loading && <LoadingState message="Mapping against OISD requirements..." />}
      {!loading && error && <p className="rounded-lg border border-critical/30 bg-critical/5 p-4 text-sm text-critical">{error}</p>}
      {!loading && data && <>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-border bg-surface p-5"><p className="text-xs text-muted">Requirements checked</p><p className="mt-2 text-3xl">{data.requirements_checked}</p></div>
          <div className="rounded-xl border border-warning/30 bg-surface p-5"><p className="text-xs text-muted">Evidence gaps</p><p className="mt-2 text-3xl text-warning">{data.summary.gaps}</p></div>
          <div className="rounded-xl border border-critical/30 bg-surface p-5"><p className="text-xs text-muted">Critical gaps</p><p className="mt-2 text-3xl text-critical">{data.summary.critical}</p></div>
        </div>
        <section className="overflow-hidden rounded-xl border border-border bg-surface">
          <div className="flex items-center justify-between border-b border-border p-5"><div><h2 className="font-semibold">OISD-118 · Tank Farm</h2><p className="text-xs text-text-secondary">Evidence matrix generated from inspection records</p></div><button className="rounded-lg bg-primary px-4 py-2 text-xs font-medium">Generate evidence package</button></div>
          <div className="overflow-x-auto"><table className="w-full min-w-[650px] text-left text-sm"><thead className="bg-card text-xs uppercase tracking-wider text-muted"><tr><th className="p-4">Clause</th><th>Requirement</th><th>Source evidence</th><th>Status</th></tr></thead><tbody>{data.matrix.slice(0, 8).map((row) => <tr className="border-t border-border" key={row.clause}><td className="p-4 font-mono text-primary">{row.clause}</td><td>{row.requirement}</td><td className="text-text-secondary">{row.evidence || row.evidence_source || "No source recorded"}</td><td><StatusBadge tone={row.status === "CRITICAL" ? "red" : row.status === "GAP" ? "amber" : "green"}>{row.status}</StatusBadge></td></tr>)}</tbody></table></div>
        </section>
      </>}
    </div>
  );
}
