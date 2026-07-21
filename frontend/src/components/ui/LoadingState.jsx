export default function LoadingState({ message }) {
  return (
    <div className="flex h-48 flex-col items-center justify-center gap-3">
      <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      <p className="font-mono text-xs text-muted">{message}</p>
    </div>
  );
}
