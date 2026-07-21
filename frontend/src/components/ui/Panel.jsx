export default function Panel({ title, description, action, children, className = "", flush = false }) {
  return (
    <section className={`overflow-hidden rounded-lg border border-border bg-surface shadow-panel ${className}`}>
      {(title || description || action) && (
        <div className="flex items-start justify-between gap-4 border-b border-border px-5 py-4">
          <div>{title && <h2 className="text-sm font-semibold text-text-primary">{title}</h2>}{description && <p className="mt-1 text-xs leading-5 text-text-secondary">{description}</p>}</div>
          {action}
        </div>
      )}
      <div className={flush ? "" : "p-5"}>{children}</div>
    </section>
  );
}