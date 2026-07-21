import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function HealthTimeline({ intervals = [] }) {
  const data = intervals.map((days, index) => ({ sequence: index + 1, days }));
  if (!data.length) return <p className="py-16 text-center text-sm text-text-secondary">At least two dated records are required to calculate failure intervals.</p>;
  return (
    <div className="h-52 w-full" role="img" aria-label="Observed days between recorded failures">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 8, right: 8, left: -12, bottom: 0 }}>
          <defs><linearGradient id="intervalFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#F59E0B" stopOpacity={0.65} /><stop offset="100%" stopColor="#F59E0B" stopOpacity={0.08} /></linearGradient></defs>
          <CartesianGrid stroke="#374151" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="sequence" stroke="#6B7280" tickLine={false} axisLine={false} tick={{ fontSize: 11 }} label={{ value: "Interval sequence", position: "insideBottom", offset: -2 }} />
          <YAxis stroke="#6B7280" tickLine={false} axisLine={false} tick={{ fontSize: 11 }} />
          <Tooltip contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }} formatter={(value) => [`${value} days`, "Observed interval"]} />
          <Area type="monotone" dataKey="days" stroke="#F59E0B" strokeWidth={2} fill="url(#intervalFill)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
