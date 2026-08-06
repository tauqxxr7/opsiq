# OPSIQ enterprise UI review

QA was completed locally at 1440 x 900 and 390 x 844 against FastAPI. Screenshots are stored in `docs/screenshots/enterprise-redesign/`.

| Workspace | Route | Desktop | Mobile | API | Issues fixed / notes |
|---|---|---|---|---|---|
| Operations overview | `/dashboard` | Pass | Pass | Local pass; preview blocked | Fleet, risk, reliability, compliance and document metrics are explicitly synthetic. |
| Asset monitor | `/assets` | Pass | Pass | Local pass; preview blocked | Five simulated assets render without chart or page overflow. |
| Expert Copilot | `/copilot` | Pass | Pass | Local ready; preview blocked | Evidence-only empty state is intentional; no unsupported answer is generated. |
| Maintenance intelligence | `/maintenance` | Pass | Pass | Local pass; preview blocked | P-201 deterministic risk, evidence and chart render cleanly. |
| Incident operations | `/incidents` | Pass | Pass | Local pass; preview blocked | Persistent incident register, filters and creation form are responsive. |
| Reliability analytics | `/reliability` | Pass | Pass | Local pass; preview blocked | Derived metrics and responsive charts render without label collisions. |
| Compliance audit | `/compliance` | Pass | Pass | Local pass; preview blocked | OISD-118 matrix and prototype disclaimer remain visible. |
| Work orders | `/work-orders` | Pass | Pass | Local pass; preview blocked | Persistent linked workflow and approval controls are role-aware. |
| Failure patterns | `/patterns` | Pass | Pass | Local pass; preview blocked | Ranked correlations and evidence table remain horizontally contained. |
| Knowledge base | `/documents` | Pass | Pass | Local pass; preview blocked | Empty inventory and upload limits are explicit. |
| Benchmarks | `/benchmarks` | Pass | Pass | Local ready; preview blocked | Values appear only after a measured run; history is not persisted. |
| Audit trail | `/audit` | Pass | Pass | Local pass; preview blocked | Process-local audit events render without overflow. |
| Settings | `/settings` | Pass | Pass | Local admin pass; preview blocked | User administration is available only to Administrators when auth is enabled. |
| Architecture | `/architecture` | Pass | Pass | Static | Direct route renders without page-level horizontal overflow. |

## Final release-candidate preview

- Preview: `https://opsiq-git-feat-enterprise-fro-b349fa-tauqeers-projects-b2ec7057.vercel.app`
- Commit: `cb32508907b99e221b2a67943827a791707a9888`
- Vercel deployment: Ready and all 14 direct SPA routes render.
- Route overflow: none observed during the final route sweep.
- Console: no OPSIQ warnings or errors were captured.
- API/CORS: blocked. Every API-backed route reports `Offline` or `The backend is unavailable` from the immutable preview origin.
- Authentication: blocked. The preview displays `Local development / Administrator`; login and frontend route guards are not production-enabled.
- Final preview status: **not ready for merge**.

## Interaction and accessibility checks

- Mobile drawer opens and closes without viewport overflow.
- Command palette, skip navigation, visible focus styles and semantic landmarks remain available.
- Loading, empty, degraded and disconnected states preserve page context.
- Reduced-motion CSS disables non-essential movement and smooth scrolling.

## Remaining limitations

- Operational records and telemetry are synthetic demonstrations, not SCADA or DCS data.
- Compliance output is evidence-gap decision support, not certification.
- Benchmark history is not persisted.
- Copilot requires indexed evidence and configured model credentials.
- Preview authentication, Railway connectivity and Railway volume persistence still require deployment-level verification.
