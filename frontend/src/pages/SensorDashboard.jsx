import { Activity, AlertTriangle, CheckCircle2, Siren } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Line, LineChart, ResponsiveContainer } from "recharts";
import { tokens } from "../design/tokens";
import { Link } from "react-router-dom";
import LoadingState from "../components/ui/LoadingState";
import MetricCard from "../components/ui/MetricCard";
import PageHeader from "../components/ui/PageHeader";
import Panel from "../components/ui/Panel";
import StatusBadge from "../components/ui/StatusBadge";
import { ErrorState, EmptyState } from "../components/ui/StatePanel";
import { activeAlarms, fleetStatus, getApiErrorMessage, sensorTrend } from "../services/api";

const tone = { CRITICAL: "red", WARNING: "amber", NORMAL: "green" };

export default function SensorDashboard() {
  const [fleet, setFleet] = useState(null), [alarms, setAlarms] = useState([]), [trends, setTrends] = useState({}), [error, setError] = useState(""), [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    try {
      const [fleetData, alarmData] = await Promise.all([fleetStatus(), activeAlarms()]);
      const trendData = await Promise.all(fleetData.equipment.map((item) => sensorTrend(item.equipment_id, 6)));
      setFleet(fleetData); setAlarms(alarmData.alarms); setTrends(Object.fromEntries(trendData.map((item) => [item.equipment_id, item.readings]))); setError("");
    } catch (requestError) { setError(getApiErrorMessage(requestError)); } finally { setLoading(false); }
  }, []);
  useEffect(() => { load(); const timer = setInterval(load, 10000); return () => clearInterval(timer); }, [load]);

  if (loading) return <div className="space-y-6"><PageHeader eyebrow="Operations telemetry" title="Asset monitor" description="Loading simulated fleet telemetry..." /><Panel><LoadingState message="Reading simulated fleet telemetry..." /></Panel></div>;
  if (error && !fleet) return <div className="space-y-6"><PageHeader eyebrow="Operations telemetry" title="Asset monitor" description="Simulated telemetry; not connected to SCADA or DCS." /><ErrorState message={error} onRetry={load} /></div>;
  return <div className="page-enter page-enter-active space-y-6">
    <PageHeader eyebrow="Operations telemetry" title="Asset monitor" description="Simulated telemetry refreshed every 10 seconds for demonstration; not connected to live SCADA." />
    {error && <ErrorState message={error} onRetry={load} />}
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricCard label="Fleet size" value={fleet.fleet_size} detail="Simulated assets" icon={Activity} />
      <MetricCard label="Critical alarms" value={fleet.critical_count} detail="Immediate review" icon={Siren} tone="text-critical" />
      <MetricCard label="Warnings" value={fleet.warning_count} detail="Threshold excursions" icon={AlertTriangle} tone="text-warning" />
      <MetricCard label="Normal assets" value={fleet.normal_count} detail="Within thresholds" icon={CheckCircle2} tone="text-secondary" />
    </div>
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{fleet.equipment.map((item) => <article key={item.equipment_id} className={`rounded-xl border bg-surface p-5 shadow-panel ${item.health_signal === "CRITICAL" ? "border-critical/50 shadow-[0_0_24px_rgba(239,68,68,.12)]" : item.health_signal === "WARNING" ? "border-warning/40" : "border-border"}`}>
      <div className="flex items-center justify-between"><h2 className="font-mono text-xl font-bold">{item.equipment_id}</h2><StatusBadge tone={tone[item.health_signal]}>{item.health_signal}</StatusBadge></div>
      <div className="my-4 h-12"><ResponsiveContainer width="100%" height="100%"><LineChart data={trends[item.equipment_id] || []}><Line type="monotone" dataKey="vibration_mm_s" stroke={tokens.color.accent} dot={false} strokeWidth={2} /></LineChart></ResponsiveContainer></div>
      <dl className="grid grid-cols-2 gap-3 text-xs"><div><dt className="text-muted">Temperature</dt><dd className="mt-1 font-mono">{item.temperature_c} deg C</dd></div><div><dt className="text-muted">Vibration</dt><dd className="mt-1 font-mono">{item.vibration_mm_s} mm/s</dd></div><div><dt className="text-muted">Bearing temp</dt><dd className="mt-1 font-mono">{item.bearing_temp_c} deg C</dd></div><div><dt className="text-muted">Speed</dt><dd className="mt-1 font-mono">{item.rpm} rpm</dd></div></dl>
      <div className="mt-4 min-h-8 text-xs text-text-secondary">{item.alarms.length ? item.alarms.map((alarm) => <p key={alarm.parameter} className="text-warning">{alarm.level}: {alarm.parameter.replaceAll("_", " ")}</p>) : "No active alarms"}</div>
      <Link to={`/maintenance?equipment=${item.equipment_id}`} className="mt-4 inline-flex rounded-lg border border-primary/30 bg-primary/10 px-3 py-2 text-xs font-semibold text-primary">View full analysis</Link>
    </article>)}</div>
    <Panel title="Active alarms" description="Current threshold excursions across the simulated fleet." flush>{alarms.length ? <div className="overflow-x-auto"><table className="data-table w-full min-w-[720px]"><thead><tr><th>Equipment</th><th>Parameter</th><th>Level</th><th>Value</th><th>Threshold</th><th>Time</th></tr></thead><tbody>{alarms.map((alarm) => <tr key={`${alarm.equipment_id}-${alarm.parameter}`}><td className="font-mono">{alarm.equipment_id}</td><td>{alarm.parameter.replaceAll("_", " ")}</td><td>{alarm.level}</td><td className="font-mono">{alarm.value}</td><td className="font-mono">{alarm.threshold}</td><td className="font-mono text-xs">{new Date(alarm.timestamp).toLocaleTimeString()}</td></tr>)}</tbody></table></div> : <EmptyState title="No active alarms" description="All simulated readings are currently within configured thresholds." />}</Panel>
  </div>;
}
