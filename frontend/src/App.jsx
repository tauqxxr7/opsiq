import { lazy, Suspense, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";

import AppShell from "./components/layout/AppShell";
import LoadingState from "./components/ui/LoadingState";

const Dashboard = lazy(() => import("./pages/Dashboard"));
const ExpertCopilot = lazy(() => import("./pages/ExpertCopilot"));
const MaintenanceIntel = lazy(() => import("./pages/MaintenanceIntel"));
const ComplianceAudit = lazy(() => import("./pages/ComplianceAudit"));
const FailurePatterns = lazy(() => import("./pages/FailurePatterns"));
const DocumentLibrary = lazy(() => import("./pages/DocumentLibrary"));
const ArchitecturePage = lazy(() => import("./pages/ArchitecturePage"));
const SensorDashboard = lazy(() => import("./pages/SensorDashboard"));
const AnalyticsPage = lazy(() => import("./pages/AnalyticsPage"));

export default function App() {
  const [open, setOpen] = useState(false);
  return (
    <AppShell navigationOpen={open} setNavigationOpen={setOpen}>
      <main className="mx-auto w-full max-w-[1600px] p-4 sm:p-6 lg:p-8">
        <Suspense fallback={<LoadingState message="Loading OPSIQ workspace..." />}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/copilot" element={<ExpertCopilot />} />
            <Route path="/maintenance" element={<MaintenanceIntel />} />
            <Route path="/compliance" element={<ComplianceAudit />} />
            <Route path="/sensors" element={<SensorDashboard />} />
            <Route path="/patterns" element={<FailurePatterns />} />
            <Route path="/documents" element={<DocumentLibrary />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/architecture" element={<ArchitecturePage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Suspense>
      </main>
    </AppShell>
  );
}
