import axios from "axios";
import { authRequired, clearTokens, getAccessToken, getRefreshToken, storeTokens } from "../auth/authStorage";
import { joinApiUrl, resolveApiBaseUrl } from "./apiConfig";

const apiBaseUrl = resolveApiBaseUrl(import.meta.env.VITE_API_URL, {
  production: import.meta.env.PROD,
});

const client = axios.create({
  timeout: 90000,
});

const endpoint = (path) => joinApiUrl(apiBaseUrl, path);
client.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (authRequired && token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
client.interceptors.response.use(undefined, async (error) => {
  const original = error.config;
  if (!authRequired || error.response?.status !== 401 || original?._retried || original?.url?.includes("auth/")) throw error;
  const refreshToken = getRefreshToken();
  if (!refreshToken) { clearTokens(); throw error; }
  original._retried = true;
  try {
    const response = await axios.post(endpoint("auth/refresh"), { refresh_token: refreshToken }, { timeout: 15000 });
    storeTokens(response.data);
    original.headers.Authorization = `Bearer ${response.data.access_token}`;
    return client(original);
  } catch (refreshError) {
    clearTokens();
    throw refreshError;
  }
});
export const health = () => client.get(apiBaseUrl.replace(/\/api$/, "/health")).then((response) => response.data);

export function getApiErrorMessage(error) {
  if (error.code === "ECONNABORTED" || error.code === "ETIMEDOUT") {
    return "The backend request timed out after 90 seconds. Please try again.";
  }
  if (!error.response) {
    return "The backend is unavailable. Check the API URL and service connectivity.";
  }
  if (error.response.status >= 500) {
    return `The backend returned server error ${error.response.status}. Please try again.`;
  }
  const detail = error.response.data?.detail;
  return detail || `The backend rejected the request (${error.response.status}). Check the submitted data.`;
}

export const ask = (payload) => client.post(endpoint("query"), payload).then((response) => response.data);
export const upload = (file, onProgress) => {
  const body = new FormData();
  body.append("file", file);
  return client.post(endpoint("documents/upload"), body, { onUploadProgress: onProgress }).then((response) => response.data);
};
export const documentStats = () => client.get(endpoint("documents/stats")).then((response) => response.data);
export const documents = () => client.get(endpoint("documents")).then((response) => response.data);
export const maintenance = (id) => client.get(endpoint(`maintenance/${id}`)).then((response) => response.data);
export const maintenanceCatalog = () => client.get(endpoint("maintenance")).then((response) => response.data);
export const compliance = (id) => client.get(endpoint(`compliance/audit/${id}`)).then((response) => response.data);
export const patterns = () => client.get(endpoint("patterns")).then((response) => response.data);

export default client;
export const fleetStatus = () => client.get(endpoint("sensors/fleet/status")).then((response) => response.data);
export const activeAlarms = () => client.get(endpoint("sensors/alarms/active")).then((response) => response.data);
export const sensorTrend = (id, hours = 6) => client.get(endpoint(`sensors/trend/${id}`), { params: { hours } }).then((response) => response.data);
export const reliabilityMetrics = () => client.get(endpoint("analytics/reliability")).then((response) => response.data);
export const downtimeTrends = () => client.get(endpoint("analytics/downtime/trends")).then((response) => response.data);
export const generateWorkOrder = (id) => client.post(endpoint(`maintenance/workorder/generate/${id}`)).then((response) => response.data);

export const similarIncidents = (payload) => client.post(endpoint("maintenance/incidents/similar"), payload).then((response) => response.data);
export const runBenchmark = () => client.get(endpoint("benchmark/run")).then((response) => response.data);
export const recentAudit = () => client.get(endpoint("audit/recent")).then((response) => response.data);
export const login = (payload) => client.post(endpoint("auth/login"), payload).then((response) => response.data);
export const authMe = () => client.get(endpoint("auth/me")).then((response) => response.data);
export const authRoles = () => client.get(endpoint("auth/roles")).then((response) => response.data);
export const authUsers = () => client.get(endpoint("auth/users")).then((response) => response.data);
export const createAuthUser = (payload) => client.post(endpoint("auth/users"), payload).then((response) => response.data);
export const incidentRecords = (params = {}) => client.get(endpoint("incidents"), { params }).then((response) => response.data);
export const createIncident = (payload) => client.post(endpoint("incidents"), payload).then((response) => response.data);
export const updateIncident = (id, payload) => client.patch(endpoint(`incidents/${id}`), payload).then((response) => response.data);
export const workOrderRecords = (params = {}) => client.get(endpoint("work-orders"), { params }).then((response) => response.data);
export const createWorkOrder = (payload) => client.post(endpoint("work-orders"), payload).then((response) => response.data);
export const updateWorkOrder = (id, payload) => client.patch(endpoint(`work-orders/${id}`), payload).then((response) => response.data);
export const approveWorkOrder = (id) => client.post(endpoint(`work-orders/${id}/approve`)).then((response) => response.data);
export const completeWorkOrder = (id, completion_notes) => client.post(endpoint(`work-orders/${id}/complete`), { completion_notes }).then((response) => response.data);
