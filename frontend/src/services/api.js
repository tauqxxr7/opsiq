import axios from "axios";
import { joinApiUrl, resolveApiBaseUrl } from "./apiConfig";

const apiBaseUrl = resolveApiBaseUrl(import.meta.env.VITE_API_URL, {
  production: import.meta.env.PROD,
});

const client = axios.create({
  timeout: 90000,
});

const endpoint = (path) => joinApiUrl(apiBaseUrl, path);

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
