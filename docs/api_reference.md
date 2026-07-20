# API Reference

Base URL: `http://localhost:8000`

## Core endpoints

- `GET /health` — liveness status.
- `POST /api/documents/upload` — multipart `file`; PDF/DOCX only.
- `GET /api/documents/stats` — current vector collection size.
- `POST /api/query` — `query` plus optional validated `query_type`, `equipment_id`, and `standard`.

## Evidence-driven analytics

### `GET /api/maintenance/{equipment_id}`

Returns a deterministic 0–100 recurrence-risk score, LOW/MONITOR/HIGH/CRITICAL level, weighted component breakdown, failure intervals, MTBF, downtime, dominant failure/root cause, evidence sufficiency, and supporting work-order IDs. Unknown equipment returns HTTP 404 with a structured no-data body.

Risk formula: recurrence frequency (25) + recent incidents (20) + severity (20) + downtime burden (15) + repeated root cause (10) + shrinking intervals (10). The endpoint does not claim a trained prediction or fabricate a time-to-failure estimate.

### `GET /api/compliance/audit/{standard}`

Derives requirement totals, compliant/gap/critical counts, compliance percentage, evidence matrix, evidence completeness, and ranked corrective actions from inspection rows. Rows without an explicit standard are documented demo records for OISD-118. An unknown standard returns a safe 200 no-data result. This is a prototype evidence-gap assessment, not legal certification.

### `GET /api/patterns`

Aggregates work orders and all recoverable incident-history records. Returns recurring equipment/failure pairs, cross-equipment root causes, high-downtime clusters, repeated precursor conditions, supporting record IDs, source counts, and a serialized weighted knowledge graph.

## Grounding contract

Knowledge-query responses include `answer`, `citations`, `confidence`, and `follow_up_suggestions`. When retrieval finds no evidence, Copilot returns exactly `Insufficient documentation found to answer safely.` with no citations and zero confidence.
