import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const healthData = [82, 80, 77, 73, 70, 67, 62, 57, 51, 46, 39, 33, 26, 19].map(
  (health, index) => ({
    day: index + 1,
    health,
  }),
);

export default function HealthTimeline() {
  return (
    <div className="h-52 w-full" role="img" aria-label="Fourteen-day asset health trend declining from 82 to 19 percent">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={healthData} margin={{ top: 8, right: 8, left: -24, bottom: 0 }}>
          <defs>
            <linearGradient id="healthFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#F59E0B" stopOpacity={0.65} />
              <stop offset="100%" stopColor="#EF4444" stopOpacity={0.08} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#374151" strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="day" stroke="#6B7280" tickLine={false} axisLine={false} tick={{ fontSize: 11 }} />
          <YAxis domain={[0, 100]} stroke="#6B7280" tickLine={false} axisLine={false} tick={{ fontSize: 11 }} />
          <Tooltip
            contentStyle={{ background: "#111827", border: "1px solid #374151", borderRadius: 8 }}
            labelStyle={{ color: "#9CA3AF" }}
            itemStyle={{ color: "#F9FAFB" }}
            formatter={(value) => [`${value}%`, "Health"]}
            labelFormatter={(day) => `Day ${day}`}
          />
          <Area type="monotone" dataKey="health" stroke="#F59E0B" strokeWidth={2} fill="url(#healthFill)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
