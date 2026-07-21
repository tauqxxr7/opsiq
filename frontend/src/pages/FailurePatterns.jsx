import { useEffect, useState } from "react";

import LoadingState from "../components/ui/LoadingState";
import { getApiErrorMessage, patterns } from "../services/api";

export default function FailurePatterns() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let ignore = false;
    patterns()
      .then((result) => { if (!ignore) setData(result); })
      .catch((requestError) => { if (!ignore) setError(getApiErrorMessage(requestError)); })
      .finally(() => { if (!ignore) setLoading(false); });
    return () => { ignore = true; };
  }, []);

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-semibold">Failure Pattern Engine</h1><p className="text-sm text-text-secondary">Cross-document incident correlation. Systemic patterns that individual reviews miss.</p></div>
      {loading && <LoadingState message="Correlating incident records..." />}
      {!loading && error && <p className="rounded-lg border border-critical/30 bg-critical/5 p-4 text-sm text-critical">{error}</p>}
      {!loading && data && <div className="grid gap-5 lg:grid-cols-2">{data.patterns.map((pattern) => <article className="rounded-xl border border-border bg-surface p-5" key={`${pattern.equipment_id}-${pattern.failure_type}`}><div className="flex justify-between"><div><p className="font-mono text-primary">{pattern.equipment_id}</p><h2 className="mt-2 font-semibold">{pattern.failure_type}</h2></div><span className={`text-xs ${pattern.risk === "CRITICAL" ? "text-critical" : "text-warning"}`}>{pattern.risk}</span></div><div className="mt-6 flex items-center gap-3"><div className="h-2 flex-1 rounded bg-border"><div className="h-full rounded bg-critical" style={{ width: `${Math.min(100, pattern.occurrences * 20)}%` }} /></div><span className="font-mono text-xs">{pattern.occurrences} events</span></div><p className="mt-4 text-xs leading-5 text-text-secondary">Shared precursor path detected: alignment drift → bearing temperature rise → seal damage.</p></article>)}</div>}
    </div>
  );
}
