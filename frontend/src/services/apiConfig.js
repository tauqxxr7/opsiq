export const LOCAL_API_BASE_URL = "http://localhost:8000/api";

export function resolveApiBaseUrl(value, { production = false } = {}) {
  const configured = value?.trim();
  if (!configured) {
    if (production) {
      console.warn(
        `VITE_API_URL is not configured; requests will use ${LOCAL_API_BASE_URL}.`,
      );
    }
    return LOCAL_API_BASE_URL;
  }

  let parsed;
  try {
    parsed = new URL(configured);
  } catch {
    throw new Error(
      "Invalid VITE_API_URL: provide an absolute URL beginning with http:// or https://.",
    );
  }

  if (!["http:", "https:"].includes(parsed.protocol) || parsed.username || parsed.password) {
    throw new Error(
      "Invalid VITE_API_URL: only absolute http:// or https:// URLs without credentials are supported.",
    );
  }
  if (parsed.search || parsed.hash) {
    throw new Error("Invalid VITE_API_URL: query strings and fragments are not supported.");
  }

  const pathname = parsed.pathname.replace(/\/+$/, "");
  parsed.pathname = pathname.endsWith("/api") ? pathname : `${pathname}/api`;
  return parsed.toString().replace(/\/+$/, "");
}

export function joinApiUrl(baseUrl, endpoint) {
  return `${baseUrl.replace(/\/+$/, "")}/${endpoint.replace(/^\/+/, "")}`;
}