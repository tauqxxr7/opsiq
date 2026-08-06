import { Activity, BarChart3, BellRing, Bot, ClipboardList, FileSearch, Gauge, LayoutDashboard, Library, Network, Settings, ShieldCheck, Wrench } from "lucide-react";
export const navigation = [
  { label: "Operations", items: [
    { to: "/dashboard", icon: LayoutDashboard, label: "Overview" }, { to: "/copilot", icon: Bot, label: "Expert Copilot" }, { to: "/assets", icon: Activity, label: "Asset Monitor" }, { to: "/maintenance", icon: Wrench, label: "Maintenance Intelligence" }, { to: "/incidents", icon: BellRing, label: "Incidents" }, { to: "/reliability", icon: Gauge, label: "Reliability" }, { to: "/compliance", icon: ShieldCheck, label: "Compliance" }, { to: "/work-orders", icon: ClipboardList, label: "Work Orders" }, { to: "/patterns", icon: Network, label: "Failure Patterns" },
  ]},
  { label: "System", items: [
    { to: "/documents", icon: Library, label: "Knowledge Base" }, { to: "/benchmarks", icon: BarChart3, label: "Benchmarks" }, { to: "/audit", icon: FileSearch, label: "Audit Trail" }, { to: "/settings", icon: Settings, label: "Settings" },
  ]},
];
