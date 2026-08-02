import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { authMe, login as loginRequest, logout as logoutRequest } from "../services/api";
import { authRequired, clearTokens, getAccessToken, getRefreshToken, storeTokens } from "./authStorage";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(authRequired ? null : { username: "system", display_name: "Local development", role: "Administrator" });
  const [checking, setChecking] = useState(authRequired && Boolean(getAccessToken()));
  useEffect(() => {
    if (!authRequired || !getAccessToken()) return;
    authMe().then(setUser).catch(() => clearTokens()).finally(() => setChecking(false));
  }, []);
  const value = useMemo(() => ({
    user, checking, authRequired,
    login: async (credentials) => { const response = await loginRequest(credentials); storeTokens(response); setUser(response.user); return response.user; },
    logout: async () => {
      const refreshToken = getRefreshToken();
      try { if (refreshToken) await logoutRequest(refreshToken); }
      catch { /* Local logout must still complete when the backend is unavailable. */ }
      finally { clearTokens(); setUser(null); }
    },
  }), [user, checking]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
