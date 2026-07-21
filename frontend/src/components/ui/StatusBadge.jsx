export default function StatusBadge({ children, tone = "green" }) {
  const styles = tone === "red" ? "bg-critical/10 text-critical" : tone === "amber" ? "bg-warning/10 text-warning" : tone === "blue" ? "bg-primary/10 text-primary" : "bg-secondary/10 text-secondary";
  return <span className={`inline-flex items-center gap-1.5 rounded px-2 py-1 text-[11px] font-semibold uppercase tracking-wide ${styles}`}><span className="h-1.5 w-1.5 rounded-full bg-current" />{children}</span>;
}