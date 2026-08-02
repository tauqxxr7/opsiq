# OPSIQ enterprise UI review

QA completed locally at 1440 x 900 and 390 x 844 against the running FastAPI service. Screenshots are stored in `docs/screenshots/enterprise-redesign/`.

| Workspace | Route | Desktop | Mobile | API | Issues fixed / notes |
|---|---|---|---|---|---|
| Operations overview | `/` | Pass | Pass | Live | Populated fleet, risk, reliability, compliance and document metrics; synthetic label visible. |
| Expert Copilot | `/copilot` | Pass | Pass | Ready | Evidence-only empty state is intentional; no unsupported answer generated. |
| Asset monitor | `/assets` | Pass | Pass | Live | Five simulated assets rendered without chart or page overflow. |
| Maintenance intelligence | `/maintenance` | Pass | Pass | Live | P-201 deterministic risk, evidence and chart rendered cleanly. |
| Incident intelligence | `/incidents` | Pass | Pass | Live | Eight API-returned similarity records verified; corrupted separator removed. |
| Reliability analytics | `/reliability` | Pass | Pass | Live | Derived metrics and responsive charts rendered without label collisions. |
| Compliance audit | `/compliance` | Pass | Pass | Live | OISD-118 evidence matrix rendered; prototype disclaimer remains visible. |
| Work orders | `/work-orders` | Pass | Pass | Live | Generated draft, evidence controls and approval warning verified; corrupted separators and bullets removed. |
| Failure patterns | `/patterns` | Pass | Pass | Live | Ranked correlations and evidence table remain horizontally contained. |
| Document library | `/documents` | Pass | Pass | Live | Backend inventory empty state and upload limits are explicit. |
| Benchmark laboratory | `/benchmarks` | Pass | Pass | Ready | No values shown until a measured benchmark is run; history is not persisted. |
| Audit trail | `/audit` | Pass | Pass | Live | Process-local events rendered; corrupted separator removed. |
| Settings | `/settings` | Pass | Pass | Read-only | Corrupted limitation bullets removed; runtime boundaries remain explicit. |

The architecture explainer at `/architecture` was also checked for routing and overflow and remains available through the command palette.

## Interaction and accessibility checks

- Mobile drawer opens and closes without viewport overflow.
- `Ctrl+K` / `Cmd+K`, skip navigation, focus styles and semantic landmarks remain available.
- Loading, empty, degraded and disconnected states preserve page context.
- Reduced-motion CSS disables non-essential movement and smooth scrolling.
- Browser console: zero warnings and zero errors during the final route sweep.

## Fixed during final visual QA

- Replaced invalid encoded separators in the persistent demo notice, incident results, work-order draft, audit description and settings limitations.
- Replaced decorative safety bullets with screen-reader-safe text markers.
- Regenerated all affected screenshots using populated API responses.

## Remaining limitations

- Operational records and telemetry are synthetic demonstrations, not SCADA or DCS data.
- Incident and work-order workflow state is not persisted.
- Compliance output is evidence-gap decision support, not certification.
- Benchmark results appear only after an explicit measured run and have no history backend.
- Copilot requires indexed evidence and configured model credentials for synthesized answers.

## Local review

Start the backend on port 8000 and run `npm run dev -- --host 127.0.0.1` from `frontend`. Review each route above at 1440 x 900 and 390 x 844, then run `npm run lint`, `npm run check:deployment` and `npm run build` before release.
