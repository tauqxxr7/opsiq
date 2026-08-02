import { lazy, Suspense, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./auth/ProtectedRoute";
import AppShell from "./components/layout/AppShell";
import { PageTransition } from "./components/motion/MotionPrimitives";
import LoadingState from "./components/ui/LoadingState";

const pages = {
  dashboard: lazy(() => import("./pages/Dashboard")), copilot: lazy(() => import("./pages/ExpertCopilot")), assets: lazy(() => import("./pages/SensorDashboard")), maintenance: lazy(() => import("./pages/MaintenanceIntel")), incidents: lazy(() => import("./pages/IncidentIntel")), reliability: lazy(() => import("./pages/AnalyticsPage")), compliance: lazy(() => import("./pages/ComplianceAudit")), workOrders: lazy(() => import("./pages/WorkOrders")), patterns: lazy(() => import("./pages/FailurePatterns")), documents: lazy(() => import("./pages/DocumentLibrary")), benchmarks: lazy(() => import("./pages/Benchmarks")), audit: lazy(() => import("./pages/AuditTrail")), settings: lazy(() => import("./pages/SettingsPage")), architecture: lazy(() => import("./pages/ArchitecturePage")), login: lazy(() => import("./pages/LoginPage")),
};
const routes = [
  ["/dashboard", pages.dashboard], ["/copilot", pages.copilot], ["/assets", pages.assets], ["/maintenance", pages.maintenance], ["/incidents", pages.incidents], ["/reliability", pages.reliability], ["/compliance", pages.compliance, ["Safety Engineer", "Supervisor", "Plant Manager", "Administrator", "Auditor"]], ["/work-orders", pages.workOrders], ["/patterns", pages.patterns, ["Reliability Engineer", "Supervisor", "Plant Manager", "Administrator", "Auditor"]], ["/documents", pages.documents], ["/benchmarks", pages.benchmarks, ["Reliability Engineer", "Administrator", "Auditor"]], ["/audit", pages.audit, ["Supervisor", "Plant Manager", "Administrator", "Auditor"]], ["/settings", pages.settings, ["Administrator"]], ["/architecture", pages.architecture],
];

function Workspace() {
  const [open, setOpen] = useState(false);
  return <ProtectedRoute><AppShell navigationOpen={open} setNavigationOpen={setOpen}><main id="main-content" className="mx-auto w-full max-w-[1800px] p-4 sm:p-6 xl:p-8"><Suspense fallback={<LoadingState message="Loading operations workspace..." />}><Routes><Route path="/" element={<Navigate to="/dashboard" replace />} />{routes.map(([path, Component, roles]) => <Route key={path} path={path} element={<ProtectedRoute roles={roles}><PageTransition><Component /></PageTransition></ProtectedRoute>} />)}<Route path="/sensors" element={<Navigate to="/assets" replace />} /><Route path="/analytics" element={<Navigate to="/reliability" replace />} /><Route path="*" element={<Navigate to="/dashboard" replace />} /></Routes></Suspense></main></AppShell></ProtectedRoute>;
}

export default function App() {
  return <Suspense fallback={<LoadingState message="Loading OPSIQ..." />}><Routes><Route path="/login" element={<pages.login />} /><Route path="*" element={<Workspace />} /></Routes></Suspense>;
}
