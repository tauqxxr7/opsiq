import axios from "axios";

const configuredApiUrl = import.meta.env.VITE_API_URL?.replace(/\/+$/, "");
const apiBaseUrl = configuredApiUrl
  ? `${configuredApiUrl}${configuredApiUrl.endsWith("/api") ? "" : "/api"}`
  : "http://localhost:8000/api";

const client = axios.create({
  baseURL: apiBaseUrl,
  timeout: 30000,
});

export function getApiErrorMessage(error) {
  if (error.code === "ECONNABORTED" || error.code === "ETIMEDOUT") {
    return "The backend request timed out after 30 seconds. Please try again.";
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

export const ask = (payload) => client.post("/query", payload).then((response) => response.data);
export const upload = (file, onProgress) => {
  const body = new FormData();
  body.append("file", file);
  return client.post("/documents/upload", body, { onUploadProgress: onProgress }).then((response) => response.data);
};
export const documentStats = () => client.get("/documents/stats").then((response) => response.data);
export const documents = () => client.get("/documents").then((response) => response.data);
export const maintenance = (id) => client.get(`/maintenance/${id}`).then((response) => response.data);
export const maintenanceCatalog = () => client.get("/maintenance").then((response) => response.data);
export const compliance = (id) => client.get(`/compliance/audit/${id}`).then((response) => response.data);
export const patterns = () => client.get("/patterns").then((response) => response.data);

export default client;
