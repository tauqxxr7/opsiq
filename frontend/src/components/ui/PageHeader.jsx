export default function PageHeader({ eyebrow, title, description, actions }) {
  return (
    <header className="flex flex-col justify-between gap-4 border-b border-border pb-6 sm:flex-row sm:items-end">
      <div className="max-w-3xl">
        {eyebrow && <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-primary">{eyebrow}</p>}
        <h1 className="mt-1 text-2xl font-semibold tracking-tight text-text-primary sm:text-[28px]">{title}</h1>
        {description && <p className="mt-2 text-sm leading-6 text-text-secondary">{description}</p>}
      </div>
      {actions && <div className="shrink-0">{actions}</div>}
    </header>
  );
}