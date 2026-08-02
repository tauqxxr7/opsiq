# OPSIQ enterprise redesign feature parity report

Comparison baseline: local `main` at `6335ff3ebab32d7de6ea6a2b64d78e43134173d1`. Comparison target: uncommitted `feat/enterprise-frontend-redesign` working tree.

## Outcome

All user-facing behavior present on `main` is available after the redesign. One accidental regression was found during this audit: the dashboard's record-level **Latest evidence** feed had been omitted. It has been restored as **Latest work-order evidence** using the same maintenance-catalog response. No feature remains classified as accidentally missing.

- **Preserved**: same interaction and backend contract.
- **Improved**: original behavior remains and gains supported presentation, resilience or workflow.
- **Moved**: behavior remains at a new primary location; legacy URLs redirect where applicable.
- **Intentionally removed**: removed deliberately with a documented reason.
- **Accidentally missing**: regression requiring restoration.

## Route parity

| Main route | Redesign route | Classification | Evidence |
|---|---|---|---|
| `/` -> `/dashboard` | `/` -> `/dashboard` | Preserved | Default entry and unknown-route fallback still resolve to the dashboard. |
| `/dashboard` | `/dashboard` | Improved | Original knowledge, maintenance, compliance and pattern signals remain; fleet, alarms and reliability context were added. |
| `/copilot` | `/copilot` | Improved | Query, citations, confidence, languages and warm-up retry remain in an evidence-focused workspace. |
| `/maintenance` | `/maintenance` | Preserved | Analysis, registry, equipment selection and embedded work-order drafting remain. |
| `/compliance` | `/compliance` | Preserved | Same OISD-118 API and evidence matrix. |
| `/sensors` | `/assets` | Moved | `/sensors` redirects to `/assets`; the same sensor page and calls remain. |
| `/patterns` | `/patterns` | Preserved | Same correlation endpoint and evidence tables. |
| `/documents` | `/documents` | Improved | Upload and inventory behavior remain under the clearer Knowledge Base navigation label. |
| `/analytics` | `/reliability` | Moved | `/analytics` redirects to `/reliability`; the same reliability and downtime calls remain. |
| `/architecture` | `/architecture` | Moved | Route remains; primary discovery moved from the sidebar to the command palette. |

New supported workspaces: `/incidents`, `/work-orders`, `/benchmarks`, `/audit`, and `/settings`.

## API parity

| API helper / endpoint family | Main behavior | Redesign behavior | Classification |
|---|---|---|---|
| `ask` / `POST query` | Copilot synthesis | Unchanged | Preserved |
| `upload` / `POST documents/upload` | Multipart upload with progress | Unchanged | Preserved |
| `documents`, `documentStats` | Inventory and index metrics | Unchanged; metrics also appear on dashboard | Improved |
| `maintenance`, `maintenanceCatalog` | Equipment analysis and registry | Unchanged; dashboard consumes the catalogue incrementally | Improved |
| `generateWorkOrder` | Draft from Maintenance | Still in Maintenance and added to standalone Work Orders | Improved |
| `compliance` | OISD-118 evidence assessment | Unchanged | Preserved |
| `patterns` | Cross-source pattern analysis | Unchanged; graph activity also summarized on dashboard | Improved |
| `fleetStatus`, `activeAlarms`, `sensorTrend` | Sensor fleet and six-hour trends | Unchanged; fleet and alarms also feed dashboard | Improved |
| `reliabilityMetrics`, `downtimeTrends` | Reliability KPIs and charts | Unchanged | Preserved |
| `health` | No frontend helper | Drives global Connected/Degraded/Offline status | Improved |
| `similarIncidents` | No frontend surface | Searchable incident workspace | Improved |
| `runBenchmark` | No frontend surface | Explicit measured benchmark execution | Improved |
| `recentAudit` | No frontend surface | Privacy-safe audit table | Improved |

API base URL validation, bounded Axios timeout and error classification remain intact. No production hostname or secret was introduced.

## Forms, filters and user actions

| Feature | Classification | Parity details |
|---|---|---|
| Copilot query form | Preserved | Text query, Enter-to-send, loading state and API errors remain. |
| Copilot suggestions | Preserved | Suggestions still populate the input without sending automatically. |
| Copilot language selector | Preserved | English, Hindi, Marathi, Tamil and Telugu remain. |
| Copilot citations/source inspector | Improved | Relevance, page/section, excerpt and confidence remain in a clearer inspector. |
| Copilot warm-up retry | Improved | Automatic 20-second retry and Retry now remain; corrupted timeout text was corrected. |
| Document upload | Preserved | PDF/DOCX selection, progress, processing result, hash and inventory refresh remain. |
| Maintenance equipment selector | Preserved | Selecting equipment still refreshes deterministic analysis. |
| Maintenance tabs and registry cards | Preserved | Risk Analysis, Equipment Registry and card-to-analysis navigation remain. |
| Maintenance work-order actions | Preserved | Generate, download and Request approval demo action remain. |
| Dashboard refresh | Improved | Seven sources load independently; partial failures no longer hide healthy panels. |
| Sensor auto-refresh | Preserved | Fleet, alarms and trends still refresh every 10 seconds. |
| Asset-to-maintenance navigation | Preserved | View full analysis still opens Maintenance with the equipment query parameter. |
| Compliance retry | Preserved | Failed OISD-118 requests retain a retry action. |
| Incident search form | Improved | Symptoms and optional equipment filter call the supported similarity endpoint. |
| Standalone work-order form | Improved | Asset draft generation and download supplement Maintenance actions. |
| Benchmark execution | Improved | Run displays endpoint-measured values and loading/error states. |
| Global navigation | Improved | Collapsible sidebar, mobile drawer and keyboard command palette supplement links. |

`main` contained the Copilot query/language controls, document picker, Maintenance equipment selector/tabs and work-order actions. All are preserved. No baseline plant, severity, status, date or table-filter controls existed on `main`; their absence is not a parity regression.

## Chart parity

| Chart | Classification | Notes |
|---|---|---|
| Asset vibration sparklines | Preserved | Same six-hour `sensorTrend` readings and Recharts line rendering. |
| Maintenance interval timeline | Preserved | Same evidence-derived intervals; no predicted date added. |
| Monthly downtime bars | Preserved | Same downtime endpoint and last-12-month series. |
| Failure-mode donut | Preserved | Same aggregation from reliability equipment metrics. |
| Dashboard health/risk bars | Improved | Additional API-derived summaries with no new chart dependency. |

## Domain capability parity

| Capability | Classification | Current behavior |
|---|---|---|
| Document upload | Preserved | Real upload API, errors, progress and indexed inventory. |
| Copilot functions | Improved | All baseline query/evidence/language/retry behavior plus clearer context. |
| Maintenance analysis | Preserved | Six-component risk, intervals, methodology, breakdown and evidence tables. |
| Sensor monitoring | Improved | Same telemetry, alarms and trends at `/assets`, with legacy redirect and dashboard reuse. |
| Compliance analysis | Preserved | Same OISD-118 score, matrix, statuses and corrective actions. |
| Failure patterns | Preserved | Same counts, graph metadata, ranked patterns and recurring root causes. |
| Benchmark execution | Improved | New frontend surface invokes the existing endpoint and shows measured values only. |
| Incident browsing | Improved | Evidence-backed similarity search is preserved and now sits beside persistent, filterable incident records. |
| Work-order drafting | Improved | Existing evidence-driven drafting remains and approved drafts can now enter a persistent, role-controlled workflow. |
| Audit information | Improved | New bounded process-local metadata view without prompts or payloads. |

## Restored regression

| Feature | Initial classification | Resolution | Final classification |
|---|---|---|---|
| Dashboard latest work-order evidence | Accidentally missing | Restored the five most recent dated records with equipment, failure mode, ID, severity and downtime. | Preserved |

## Intentional removals and remaining gaps

No functioning `main` feature was intentionally removed. Architecture was moved, while `/sensors` and `/analytics` were renamed with redirects.

Incident, work-order, approval and user persistence now use a single-instance SQLite operational store. JWT access/refresh tokens and RBAC are implemented behind environment flags. Remaining limitations are no tenancy, no refresh-token revocation, no password reset/rotation workflow, no PostgreSQL scale-out, no benchmark-history persistence and no complete real-plant incident corpus.
