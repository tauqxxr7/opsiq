import { Bot, Boxes, LayoutDashboard, Library, Network, ShieldCheck, Wrench, X } from "lucide-react";
import { NavLink } from "react-router-dom";

const links = [
  ["/", LayoutDashboard, "Overview"],
  ["/copilot", Bot, "Copilot"],
  ["/maintenance", Wrench, "Maintenance"],
  ["/compliance", ShieldCheck, "Compliance"],
  ["/patterns", Network, "Failure patterns"],
  ["/documents", Library, "Document library"],
  ["/architecture", Boxes, "Architecture"],
];

export default function Sidebar({ open, setOpen }) {
  return (
    <>
      {open && <button className="fixed inset-0 z-30 bg-slate-950/45 lg:hidden" onClick={() => setOpen(false)} aria-label="Close navigation overlay" />}
      <aside className={`${open ? "translate-x-0" : "-translate-x-full"} fixed inset-y-0 left-0 z-40 flex w-64 flex-col bg-sidebar text-white transition-transform lg:translate-x-0`} aria-label="Primary navigation">
        <div className="flex h-20 items-center justify-between border-b border-white/10 px-5">
          <div>
            <p className="text-lg font-bold tracking-[0.16em]">OPSIQ</p>
            <p className="mt-0.5 text-[10px] uppercase tracking-[0.18em] text-sidebar-muted">Industrial intelligence</p>
          </div>
          <button className="rounded-md p-2 text-sidebar-muted lg:hidden" onClick={() => setOpen(false)} aria-label="Close navigation"><X size={19} /></button>
        </div>
        <nav className="flex-1 space-y-1 px-3 py-6">
          {links.map(([to, Icon, label]) => (
            <NavLink key={to} to={to} end={to === "/"} onClick={() => setOpen(false)}
              className={({ isActive }) => `flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-colors ${isActive ? "bg-white text-sidebar shadow-sm" : "text-sidebar-muted hover:bg-white/10 hover:text-white"}`}>
              <Icon size={17} aria-hidden="true" /><span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-white/10 px-5 py-4">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-sidebar-muted">Evidence scope</p>
          <p className="mt-1 text-xs leading-5 text-white/75">Synthetic industrial demonstration data</p>
        </div>
      </aside>
    </>
  );
}