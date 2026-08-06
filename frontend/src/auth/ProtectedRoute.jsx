import { Navigate, useLocation } from "react-router-dom";
import ForbiddenPage from "../components/ForbiddenPage";
import LoadingState from "../components/ui/LoadingState";
import { useAuth } from "./AuthContext";

export default function ProtectedRoute({ children, roles }) {
  const { user, checking, authRequired } = useAuth();
  const location = useLocation();
  if (checking) return <main className="grid min-h-screen place-items-center"><LoadingState message="Verifying OPSIQ access..." /></main>;
  if (authRequired && !user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (roles?.length && user && !roles.includes(user.role)) return <ForbiddenPage role={user.role} />;
  return children;
}
