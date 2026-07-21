import { AlertTriangle, Inbox } from "lucide-react";

export function ErrorState({ message, onRetry }) {
  return <div className="rounded-lg border border-critical/25 bg-critical/5 p-5" role="alert"><div className="flex gap-3"><AlertTriangle className="mt-0.5 shrink-0 text-critical" size={18} /><div><p className="text-sm font-semibold text-critical">Unable to load current data</p><p className="mt-1 text-sm text-text-secondary">{message}</p>{onRetry && <button onClick={onRetry} className="mt-3 rounded-md border border-border bg-surface px-3 py-2 text-xs font-semibold text-text-primary hover:bg-card">Try again</button>}</div></div></div>;
}

export function EmptyState({ title = "No evidence available", description, action }) {
  return <div className="flex min-h-48 flex-col items-center justify-center px-6 text-center"><Inbox className="text-muted" size={26} /><p className="mt-3 text-sm font-semibold">{title}</p>{description && <p className="mt-1 max-w-md text-sm text-text-secondary">{description}</p>}{action && <div className="mt-4">{action}</div>}</div>;
}