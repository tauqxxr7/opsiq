export default function StatusBadge({ children, tone = "green" }) {
  const styles = tone === "red"
    ? "border-critical/30 bg-critical/15 text-critical"
    : tone === "amber"
      ? "border-warning/30 bg-warning/15 text-warning"
      : tone === "blue"
        ? "border-blue-500/30 bg-blue-500/15 text-blue-400"
        : "border-secondary/30 bg-secondary/15 text-secondary";

  return <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${styles}`}><span className="status-dot h-1.5 w-1.5 rounded-full bg-current" />{children}</span>;
}