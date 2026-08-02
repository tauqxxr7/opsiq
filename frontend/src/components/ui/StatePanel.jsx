import { AlertTriangle, Inbox } from "lucide-react";

export function ErrorState({ message, onRetry }) {
  return <div className="rounded-xl border border-critical/30 bg-critical/10 p-5" role="alert"><div className="flex gap-3"><AlertTriangle className="mt-0.5 shrink-0 text-critical" size={18} /><div><p className="text-sm font-semibold text-critical">Unable to load current data</p><p className="mt-1 text-sm leading-relaxed text-text-secondary">{message}</p>{onRetry && <button onClick={onRetry} className="mt-3 rounded-lg border border-border bg-surface px-3 py-2 text-xs font-semibold text-text-primary transition-colors hover:border-primary/40 hover:bg-card">Try again</button>}</div></div></div>;
}

export function EmptyState({ title = "No evidence available", description, action }) {
  return <div className="flex flex-col items-center justify-center gap-4 px-6 py-16 text-center"><div className="flex h-12 w-12 items-center justify-center rounded-xl border border-border bg-card"><Inbox className="text-muted" size={22} /></div><div><p className="mb-1 text-sm font-medium text-text-primary">{title}</p>{description && <p className="max-w-xs text-xs leading-relaxed text-text-secondary">{description}</p>}</div>{action}</div>;
}