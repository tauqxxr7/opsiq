# API contracts

All specialist endpoints return HTTP 200 for valid requests, including valid requests with no matching evidence. Invalid uploads use explicit 4xx statuses.

## Specialist endpoints

- `GET /api/maintenance` — evidence-backed equipment catalog and aggregate high-risk count.
- `GET /api/maintenance/{equipment_id}` — score, breakdown, recurrence metrics, evidence, limitations and reproducibility metadata.
- `GET /api/compliance/audit/{standard}` — record-derived matrix, percentage, corrective actions and evidence. Bundled data supports only `OISD-118`.
- `GET /api/patterns` — cross-source recurring patterns, root causes, downtime clusters, precursors and serialized evidence graph.

A valid query without matching records returns:

```json
{"status":"no_data","message":"...","evidence":[],"limitations":["..."]}
```

## Document endpoints

- `POST /api/documents/upload` — PDF/DOCX, maximum `MAX_UPLOAD_SIZE_MB` (20 by default).
- `GET /api/documents` — persistent ingestion manifest with filename, SHA-256, type, pages, chunks, status and timestamp.
- `GET /api/documents/stats` — vector chunk and manifest document counts.

Upload status codes: `415` unsupported type, `413` too large, `422` empty/signature mismatch/corrupt/no extractable text, `409` duplicate SHA-256.

## Traceability metadata

Successful specialist analyses include `analysis_id`, `dataset_hash`, `methodology_version`, `generated_at` and `synthetic_data`. Evidence arrays and supporting IDs identify the exact records used.
