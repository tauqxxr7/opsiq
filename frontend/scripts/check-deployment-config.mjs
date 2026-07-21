import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

import {
  LOCAL_API_BASE_URL,
  joinApiUrl,
  resolveApiBaseUrl,
} from "../src/services/apiConfig.js";

const appRoutes = [
  "/",
  "/copilot",
  "/maintenance",
  "/compliance",
  "/patterns",
  "/documents",
  "/architecture",
];

const config = JSON.parse(await readFile(new URL("../vercel.json", import.meta.url)));
const rewrites = config.rewrites ?? [];
const routeDestinations = new Map(
  rewrites.map(({ source, destination }) => [source, destination]),
);

for (const route of appRoutes) {
  assert.equal(routeDestinations.get(route), "/index.html", `Missing SPA rewrite for ${route}`);
}
assert.equal(
  rewrites.some(({ source }) => source.includes("assets") || source.includes(":path")),
  false,
  "Static assets must not be captured by the SPA rewrite",
);

assert.equal(resolveApiBaseUrl(undefined), LOCAL_API_BASE_URL);
assert.equal(
  resolveApiBaseUrl("https://backend.example.com"),
  "https://backend.example.com/api",
);
assert.equal(
  resolveApiBaseUrl("https://backend.example.com/api/"),
  "https://backend.example.com/api",
);
assert.throws(
  () => resolveApiBaseUrl("backend.example.com"),
  /absolute URL/,
);
assert.equal(
  joinApiUrl("https://backend.example.com/api/", "/maintenance/P-201"),
  "https://backend.example.com/api/maintenance/P-201",
);

console.log("Deployment configuration checks passed.");