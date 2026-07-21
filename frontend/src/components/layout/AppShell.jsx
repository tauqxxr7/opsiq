import Sidebar from "./Sidebar";
import TopBar from "./TopBar";

export default function AppShell({ children, navigationOpen, setNavigationOpen }) {
  return (
    <div className="min-h-screen bg-base">
      <Sidebar open={navigationOpen} setOpen={setNavigationOpen} />
      <div className="min-h-screen lg:pl-64">
        <TopBar setOpen={setNavigationOpen} />
        {children}
      </div>
    </div>
  );
}