import {
  Bot,
  Boxes,
  LayoutDashboard,
  Library,
  Network,
  ShieldCheck,
  Wrench,
  X,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const links = [
  ["/", LayoutDashboard, "Command Centre", "Plant risk overview"],
  ["/copilot", Bot, "Expert Copilot", "Ask your documents"],
  ["/maintenance", Wrench, "Maintenance Intel", "Equipment health analytics"],
  ["/compliance", ShieldCheck, "Compliance Audit", "OISD · Factory Act · PESO"],
  ["/patterns", Network, "Failure Patterns", "Cross-asset correlation"],
  ["/documents", Library, "Document Library", "Knowledge ingestion"],
  ["/architecture", Boxes, "Architecture", "System design"],
];

export default function Sidebar({ open, setOpen }) {
  return (
    <aside className={`${open ? "translate-x-0" : "-translate-x-full"} fixed inset-y-0 left-0 z-30 w-72 border-r border-border bg-surface p-5 transition md:translate-x-0`}>
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xl font-bold tracking-[.18em]">OPSIQ</div>
          <div className="text-[10px] uppercase tracking-widest text-text-secondary">Industrial Intelligence</div>
        </div>
        <button className="md:hidden" onClick={() => setOpen(false)} aria-label="Close navigation"><X /></button>
      </div>
      <nav className="mt-10 space-y-1">
        {links.map(([to, Icon, label, subtitle]) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            title={subtitle}
            aria-label={`${label}: ${subtitle}`}
            onClick={() => setOpen(false)}
            className={({ isActive }) => `flex items-center gap-3 rounded-lg px-3 py-3 text-sm ${isActive ? "bg-primary/15 text-primary" : "text-text-secondary hover:bg-card hover:text-text-primary"}`}
          >
            <Icon size={17} />{label}
          </NavLink>
        ))}
      </nav>
      <div className="absolute bottom-5 left-5 right-5 rounded-lg border border-secondary/20 bg-secondary/5 p-3 text-xs">
        <div className="flex items-center gap-2 text-secondary"><span className="h-2 w-2 animate-pulse rounded-full bg-secondary" />All systems operational</div>
        <p className="mt-2 text-text-secondary">OPSIQ v1.0 · Synthetic Demo Mode</p>
      </div>
    </aside>
  );
}
