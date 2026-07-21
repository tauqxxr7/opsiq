import { Menu } from "lucide-react";

export default function TopBar({ setOpen }) {
  return (
    <header className="sticky top-0 z-20 flex h-16 items-center border-b border-border bg-surface/95 px-4 backdrop-blur sm:px-6 lg:px-8">
      <button className="rounded-md p-2 text-text-secondary lg:hidden" onClick={() => setOpen(true)} aria-label="Open navigation">
        <Menu size={20} />
      </button>
      <div className="ml-3 lg:ml-0">
        <p className="text-sm font-semibold text-text-primary">Operations intelligence workspace</p>
        <p className="hidden text-xs text-muted sm:block">Evidence-derived analytics · synthetic demonstration data</p>
      </div>
      <span className="ml-auto rounded-md bg-card px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide text-text-secondary">Demo environment</span>
    </header>
  );
}