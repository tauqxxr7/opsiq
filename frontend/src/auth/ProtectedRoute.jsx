import { Navigate, useLocation } from "react-router-dom";
import LoadingState from "../components/ui/LoadingState";
import { useAuth } from "./AuthContext";

export default function ProtectedRoute({ children, roles }) {
  const { user, checking, authRequired } = useAuth();
  const location = useLocation();
  if (checking) return <main className="grid min-h-screen place-items-center"><LoadingState message="Verifying OPSIQ access..." /></main>;
  if (authRequired && !user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (roles?.length && user && !roles.includes(user.role)) return <main className="grid min-h-screen place-items-center p-6"><div className="max-w-md rounded-xl border border-critical/30 bg-surface p-6"><h1 className="text-xl font-semibold">Access restricted</h1><p className="mt-2 text-sm text-text-secondary">Your {user.role} role does not permit this workspace.</p></div></main>;
  return children;
}
