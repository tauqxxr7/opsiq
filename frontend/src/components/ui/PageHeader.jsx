export default function PageHeader({ eyebrow, title, description, actions }) {
  return (
    <header className="mb-6">
      <div className="mb-4 h-px bg-gradient-to-r from-primary/50 via-primary/20 to-transparent" />
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div className="max-w-3xl">
          {eyebrow && <p className="mb-1 text-xs font-medium uppercase tracking-widest text-muted">{eyebrow}</p>}
          <h1 className="text-2xl font-semibold tracking-tight text-text-primary">{title}</h1>
          {description && <p className="mt-1 text-sm leading-relaxed text-text-secondary">{description}</p>}
        </div>
        {actions && <div className="shrink-0">{actions}</div>}
      </div>
    </header>
  );
}
