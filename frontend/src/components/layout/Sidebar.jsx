import { Activity, BarChart3, Bot, Boxes, LayoutDashboard, Library, Network, ShieldCheck, Wrench, X } from "lucide-react";
import { NavLink } from "react-router-dom";

const links = [
  ["/dashboard", LayoutDashboard, "Overview"],
  ["/copilot", Bot, "Copilot"],
  ["/maintenance", Wrench, "Maintenance"],
  ["/compliance", ShieldCheck, "Compliance"],
  ["/sensors", Activity, "Sensor monitor"],
  ["/patterns", Network, "Failure patterns"],
  ["/documents", Library, "Document library"],
  ["/analytics", BarChart3, "Analytics"],
  ["/architecture", Boxes, "Architecture"],
];

export default function Sidebar({ open, setOpen }) {
  return (
    <>
      {open && <button className="fixed inset-0 z-30 bg-slate-950/70 backdrop-blur-sm lg:hidden" onClick={() => setOpen(false)} aria-label="Close navigation overlay" />}
      <aside className={`${open ? "translate-x-0" : "-translate-x-full"} fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-border/70 bg-sidebar text-text-primary transition-transform lg:translate-x-0`} aria-label="Primary navigation">
        <div className="flex h-20 items-center justify-between border-b border-border/70 px-5">
          <div>
            <p className="text-lg font-bold tracking-[0.16em]">OPSIQ</p>
            <p className="mt-0.5 text-[10px] uppercase tracking-[0.18em] text-sidebar-muted">Industrial intelligence</p>
          </div>
          <button className="rounded-md p-2 text-sidebar-muted lg:hidden" onClick={() => setOpen(false)} aria-label="Close navigation"><X size={19} /></button>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-6">
          {links.map(([to, Icon, label]) => (
            <NavLink key={to} to={to} onClick={() => setOpen(false)} className={({ isActive }) => `group flex items-center gap-3 rounded-lg border px-3 py-2.5 text-sm transition-all duration-150 ${isActive ? "nav-active border-primary/20 bg-primary/10 font-medium text-primary shadow-[0_0_12px_rgba(59,130,246,0.15)]" : "border-transparent text-text-secondary hover:bg-card hover:text-text-primary"}`}>
              <span className="flex h-5 w-5 items-center justify-center opacity-70 transition-opacity group-hover:opacity-100"><Icon size={17} aria-hidden="true" /></span><span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-border/70 px-5 py-4">
          <p className="text-xs font-semibold uppercase tracking-widest text-sidebar-muted">Evidence scope</p>
          <p className="mt-1 text-xs leading-relaxed text-text-secondary">Synthetic industrial demonstration data</p>
        </div>
      </aside>
    </>
  );
}
