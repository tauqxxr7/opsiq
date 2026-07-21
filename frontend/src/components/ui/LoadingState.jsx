export default function LoadingState({ message = "Loading current evidence..." }) {
  return (
    <div className="space-y-4 py-3" role="status" aria-live="polite">
      <span className="sr-only">{message}</span>
      <div className="h-4 w-44 animate-pulse rounded bg-border" />
      <div className="grid gap-3 sm:grid-cols-3">
        {[0, 1, 2].map((item) => <div key={item} className="h-24 animate-pulse rounded-lg bg-card" />)}
      </div>
      <div className="space-y-2">{[0, 1, 2].map((item) => <div key={item} className="h-10 animate-pulse rounded bg-card" />)}</div>
    </div>
  );
}