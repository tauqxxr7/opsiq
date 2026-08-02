import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { authMe, login as loginRequest } from "../services/api";
import { authRequired, clearTokens, getAccessToken, storeTokens } from "./authStorage";

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
    logout: () => { clearTokens(); setUser(null); },
  }), [user, checking]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
