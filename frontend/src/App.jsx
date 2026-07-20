import { lazy, Suspense, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import Sidebar from "./components/layout/Sidebar";
import TopBar from "./components/layout/TopBar";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const ExpertCopilot = lazy(() => import("./pages/ExpertCopilot"));
const MaintenanceIntel = lazy(() => import("./pages/MaintenanceIntel"));
const ComplianceAudit = lazy(() => import("./pages/ComplianceAudit"));
const FailurePatterns = lazy(() => import("./pages/FailurePatterns"));
const DocumentLibrary = lazy(() => import("./pages/DocumentLibrary"));
const ArchitecturePage = lazy(() => import("./pages/ArchitecturePage"));

export default function App() {
  const [open, setOpen] = useState(false);

  return (
    <div className="min-h-screen bg-base">
      <Sidebar open={open} setOpen={setOpen} />
      <div className="md:pl-72">
        <TopBar setOpen={setOpen} />
        <main className="p-4 md:p-8">
          <Suspense
            fallback={
              <div className="flex h-full items-center justify-center">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              </div>
            }
          >
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/copilot" element={<ExpertCopilot />} />
              <Route path="/maintenance" element={<MaintenanceIntel />} />
              <Route path="/compliance" element={<ComplianceAudit />} />
              <Route path="/patterns" element={<FailurePatterns />} />
              <Route path="/documents" element={<DocumentLibrary />} />
              <Route path="/architecture" element={<ArchitecturePage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </main>
      </div>
    </div>
  );
}
