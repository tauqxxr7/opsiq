
export default function StatusBadge({children,tone="green"}){const c=tone==="red"?"border-critical/30 bg-critical/10 text-critical":tone==="amber"?"border-warning/30 bg-warning/10 text-warning":"border-secondary/30 bg-secondary/10 text-secondary";return <span className={"inline-flex rounded-full border px-2.5 py-1 text-xs font-medium "+c}>{children}</span>}
