import { useEffect, useState } from "react";
import CommandPalette from "../navigation/CommandPalette";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";
export default function AppShell({ children, navigationOpen, setNavigationOpen }) {
  const [collapsed, setCollapsed] = useState(false), [commandOpen, setCommandOpen] = useState(false);
  useEffect(() => { const handler = (event) => { if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") { event.preventDefault(); setCommandOpen(true); } if (event.key === "Escape") setCommandOpen(false); }; addEventListener("keydown", handler); return () => removeEventListener("keydown", handler); }, []);
  return <div className="min-h-screen bg-base"><a href="#main-content" className="skip-link">Skip to content</a><Sidebar open={navigationOpen} setOpen={setNavigationOpen} collapsed={collapsed} setCollapsed={setCollapsed} /><div className={`min-h-screen transition-[padding] duration-200 ${collapsed ? "lg:pl-[76px]" : "lg:pl-72"}`}><TopBar setOpen={setNavigationOpen} openCommand={() => setCommandOpen(true)} />{children}</div><CommandPalette open={commandOpen} onClose={() => setCommandOpen(false)} /></div>;
}
