import { Activity, ArrowUpRight, Files, ShieldCheck, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";

import workOrders from "../../../backend/data/synthetic/work_orders.json";
import MetricCard from "../components/ui/MetricCard";
import { documentStats, maintenance } from "../services/api";

const equipmentIds = [...new Set(workOrders.map((record) => record.equipment_id))];
const feedItems = workOrders
  .filter((record) => ["HIGH", "CRITICAL"].includes(record.severity))
  .sort((left, right) => new Date(right.date) - new Date(left.date))
  .slice(0, 4);

function relativeDate(date) {
  const days = Math.round((new Date(date).getTime() - Date.now()) / 86_400_000);
  const formatter = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
  if (Math.abs(days) < 30) return formatter.format(days, "day");
  const months = Math.round(days / 30);
  if (Math.abs(months) < 12) return formatter.format(months, "month");
  return formatter.format(Math.round(months / 12), "year");
}

function feedTone(severity) {
  if (severity === "CRITICAL") return "bg-critical";
  if (severity === "HIGH") return "bg-warning";
  return "bg-secondary";
}

export default function Dashboard() {
  const [chunkCount, setChunkCount] = useState(null);
  const [activeAlerts, setActiveAlerts] = useState(null);
  const compliancePosture = globalThis.localStorage?.getItem("opsiq:compliance-posture");

  useEffect(() => {
    let ignore = false;
    documentStats()
      .then((data) => { if (!ignore) setChunkCount(data.chunks); })
      .catch(() => { if (!ignore) setChunkCount("Unavailable"); });

    Promise.allSettled(equipmentIds.map((equipmentId) => maintenance(equipmentId)))
      .then((results) => {
        if (ignore) return;
        const successfulResults = results.filter((result) => result.status === "fulfilled");
        if (successfulResults.length === 0) {
          setActiveAlerts("Unavailable");
          return;
        }
        const alertCount = successfulResults.filter((result) => ["HIGH", "CRITICAL"].includes(result.value.risk_level)).length;
        setActiveAlerts(alertCount);
      });
    return () => { ignore = true; };
  }, []);

  return (
    <div className="space-y-7">
      <div className="flex flex-col justify-between gap-4 sm:flex-row">
        <div>
          <p className="text-xs uppercase tracking-[.2em] text-primary">Plant risk overview</p>
          <h1 className="mt-2 text-2xl font-semibold">Command Centre</h1>
          <p className="mt-1 text-sm text-text-secondary">Operational knowledge, risk and compliance in one evidence layer.</p>
        </div>
        <div className="flex items-center gap-2 self-start rounded-full border border-secondary/20 bg-secondary/5 px-3 py-2 text-xs text-secondary"><span className="h-2 w-2 animate-pulse rounded-full bg-secondary" />Live · Synthetic Demo</div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Indexed knowledge" value={chunkCount ?? "…"} detail="Actual indexed chunk count" icon={Files} />
        <MetricCard label="Assets monitored" value={equipmentIds.length} detail="Unique work-order equipment IDs" icon={Activity} tone="text-secondary" />
        <MetricCard label="Compliance posture" value={compliancePosture ? `${compliancePosture}%` : "Run audit to calculate"} detail={compliancePosture ? "Derived from latest audit" : "No audit result stored"} icon={ShieldCheck} tone="text-warning" />
        <MetricCard label="Active alerts" value={activeAlerts ?? "…"} detail="HIGH / CRITICAL equipment" icon={TriangleAlert} tone="text-critical" />
      </div>

      <div className="grid gap-5 xl:grid-cols-3">
        <section className="rounded-xl border border-border bg-surface p-5 xl:col-span-2">
          <div className="flex justify-between"><h2 className="font-semibold">Asset risk signal</h2><span className="font-mono text-xs text-text-secondary">14-day horizon</span></div>
          <div className="mt-6 flex h-56 items-end gap-2">{[64, 61, 58, 56, 52, 50, 47, 44, 40, 37, 33, 29, 25, 19].map((value, index) => <div key={`${value}-${index}`} className="flex-1 rounded-t bg-primary/60 hover:bg-primary" style={{ height: `${value}%` }} />)}</div>
          <div className="mt-3 flex justify-between text-xs text-muted"><span>04 Jul</span><span className="text-critical">P-201 health degrading</span><span>18 Jul</span></div>
        </section>
        <section className="rounded-xl border border-border bg-surface p-5">
          <h2 className="font-semibold">Intelligence feed</h2>
          <div className="mt-4 divide-y divide-border">
            {feedItems.map((record) => (
              <div className="py-4" key={record.wo_id} title={record.date}>
                <div className="flex gap-3">
                  <span className={`mt-1 h-2 w-2 rounded-full ${feedTone(record.severity)}`} />
                  <div><p className="text-sm">{record.equipment_id} — {record.failure_type}</p><p className="mt-1 text-xs text-muted">{relativeDate(record.date)}</p></div>
                  <ArrowUpRight className="ml-auto text-muted" size={14} />
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
