export default function Panel({ title, description, action, children, className = "", flush = false }) {
  return (
    <section className={`card-hover overflow-hidden rounded-xl border border-border bg-surface shadow-panel ${className}`}>
      {(title || description || action) && (
        <div className="flex items-start justify-between gap-4 border-b border-border/70 px-5 py-4">
          <div>
            {title && <h2 className="text-xs font-semibold uppercase tracking-widest text-muted">{title}</h2>}
            {description && <p className="mt-2 text-sm leading-relaxed text-text-secondary">{description}</p>}
          </div>
          {action}
        </div>
      )}
      <div className={flush ? "" : "p-5"}>{children}</div>
    </section>
  );
}
