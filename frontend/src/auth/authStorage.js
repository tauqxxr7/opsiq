const ACCESS_KEY = "opsiq_access_token";
const REFRESH_KEY = "opsiq_refresh_token";

export const authRequired = import.meta.env.VITE_AUTH_REQUIRED === "true";
export const getAccessToken = () => sessionStorage.getItem(ACCESS_KEY);
export const getRefreshToken = () => sessionStorage.getItem(REFRESH_KEY);
export const storeTokens = ({ access_token, refresh_token }) => {
  sessionStorage.setItem(ACCESS_KEY, access_token);
  sessionStorage.setItem(REFRESH_KEY, refresh_token);
};
export const clearTokens = () => {
  sessionStorage.removeItem(ACCESS_KEY);
  sessionStorage.removeItem(REFRESH_KEY);
};
