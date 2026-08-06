import { LockKeyhole } from "lucide-react";
import { useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { getApiErrorMessage } from "../services/api";

export default function LoginPage() {
  const { user, login, authRequired } = useAuth();
  const [username, setUsername] = useState(""), [password, setPassword] = useState(""), [error, setError] = useState(""), [busy, setBusy] = useState(false);
  const navigate = useNavigate(), location = useLocation();
  if (!authRequired || user) return <Navigate to="/dashboard" replace />;
  const submit = async (event) => { event.preventDefault(); setBusy(true); setError(""); try { await login({ username, password }); navigate(location.state?.from || "/dashboard", { replace: true }); } catch (requestError) { setError(getApiErrorMessage(requestError)); } finally { setBusy(false); } };
  return <main className="grid min-h-screen place-items-center bg-background p-6"><form onSubmit={submit} className="w-full max-w-md rounded-2xl border border-border bg-surface p-7 shadow-panel"><div className="mb-6 flex items-center gap-3"><span className="grid h-11 w-11 place-items-center rounded-xl border border-primary/30 bg-primary/10 text-primary"><LockKeyhole size={20} /></span><div><p className="section-label">Protected operations</p><h1 className="text-2xl font-semibold">Sign in to OPSIQ</h1></div></div><label className="section-label" htmlFor="username">Username</label><input id="username" autoComplete="username" className="field mt-2 w-full" value={username} onChange={(event) => setUsername(event.target.value)} required /><label className="section-label mt-5 block" htmlFor="password">Password</label><input id="password" type="password" autoComplete="current-password" className="field mt-2 w-full" value={password} onChange={(event) => setPassword(event.target.value)} required />{error ? <p role="alert" className="mt-4 text-sm text-critical">{error}</p> : null}<button className="primary-button mt-6 w-full justify-center" disabled={busy}>{busy ? "Signing in..." : "Sign in"}</button><p className="mt-4 text-xs leading-5 text-muted">Credentials are configured through backend environment variables. Passwords are stored as scrypt hashes.</p></form></main>;
}
