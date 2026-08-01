import { Activity, Clock3, Gauge, TriangleAlert } from "lucide-react";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import LoadingState from "../components/ui/LoadingState";
import MetricCard from "../components/ui/MetricCard";
import PageHeader from "../components/ui/PageHeader";
import Panel from "../components/ui/Panel";
import { ErrorState } from "../components/ui/StatePanel";
import { downtimeTrends, getApiErrorMessage, reliabilityMetrics } from "../services/api";

export default function AnalyticsPage() {
  const [data, setData] = useState(null), [trends, setTrends] = useState([]), [error, setError] = useState("");
  useEffect(() => { Promise.all([reliabilityMetrics(), downtimeTrends()]).then(([metrics, trend]) => { setData(metrics); setTrends(trend.monthly_downtime); }).catch((requestError) => setError(getApiErrorMessage(requestError))); }, []);
  if (error) return <ErrorState message={error} />;
  if (!data) return <Panel><LoadingState message="Computing reliability metrics..." /></Panel>;
  const summary = data.fleet_summary;
  const failures = Object.entries(data.equipment_metrics.reduce((counts, item) => ({ ...counts, [item.most_common_failure]: (counts[item.most_common_failure] || 0) + item.total_failures }), {})).map(([name, value]) => ({ name, value }));
  return <div className="page-enter page-enter-active space-y-6">
    <PageHeader eyebrow="Reliability engineering" title="Fleet analytics" description="Derived from synthetic work-order dates and downtime; availability is an illustrative estimate." />
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><MetricCard label="Assets analysed" value={summary.total_equipment_analysed} detail="Evidence-backed fleet" icon={Activity} /><MetricCard label="Total failures" value={summary.total_failures} detail="Recorded events" icon={TriangleAlert} tone="text-warning" /><MetricCard label="Average MTBF" value={`${summary.fleet_average_mtbf_days} d`} detail="Mean dated interval" icon={Gauge} /><MetricCard label="Average MTTR" value={`${summary.fleet_average_mttr_hours} h`} detail="Mean downtime" icon={Clock3} /></div>
    <div className="grid gap-6 xl:grid-cols-2"><Panel title="Monthly downtime" description="Last 12 recorded months"><div className="h-72"><ResponsiveContainer><BarChart data={trends}><CartesianGrid stroke="#374151" vertical={false} /><XAxis dataKey="month" tick={{ fill: "#9CA3AF", fontSize: 11 }} /><YAxis tick={{ fill: "#9CA3AF", fontSize: 11 }} /><Tooltip /><Bar dataKey="downtime_hours" fill="#3B82F6" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></div></Panel><Panel title="Failure modes" description="Failure records grouped by dominant equipment mode"><div className="h-72"><ResponsiveContainer><PieChart><Pie data={failures} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} fill="#34D399" label /><Tooltip /></PieChart></ResponsiveContainer></div></Panel></div>
    <Panel title="MTBF / MTTR by equipment" description={`Highest downtime asset: ${summary.highest_risk_asset}`} flush><div className="overflow-x-auto"><table className="data-table w-full min-w-[760px]"><thead><tr><th>Equipment</th><th>Failures</th><th>Downtime</th><th>MTBF</th><th>MTTR</th><th>Availability estimate</th></tr></thead><tbody>{data.equipment_metrics.map((item) => <tr key={item.equipment_id} className={item.equipment_id === summary.highest_risk_asset ? "bg-critical/10" : ""}><td className="font-mono font-semibold">{item.equipment_id}</td><td>{item.total_failures}</td><td>{item.total_downtime_hours} h</td><td>{item.mtbf_days} d</td><td>{item.mttr_hours} h</td><td>{item.availability_estimate_pct}%</td></tr>)}</tbody></table></div></Panel>
  </div>;
}
