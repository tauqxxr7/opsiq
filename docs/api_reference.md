# API reference

Local base URL: `http://localhost:8000`  
Production API documentation: [Swagger UI](https://opsiq-production-b20c.up.railway.app/docs)

All specialist datasets are synthetic demonstrations.

## Health

**GET `/health`** — liveness check.

```json
{"status":"operational","service":"OPSIQ"}
```

Returns HTTP 200 while the service is available. It does not require Gemini credentials.

## Maintenance

**GET `/api/maintenance/{equipment_id}`** — deterministic historical recurrence-risk analysis.

Example: `GET /api/maintenance/P-201`

A successful response includes `status`, `equipment_id`, recurrence-risk score and level, score components, recurrence intervals, supporting work-order evidence, methodology version, analysis ID, dataset hash, and limitations. It does not include a predicted failure date.

Unknown equipment returns HTTP 200 with `status: "no_data"`, the requested ID, and an explanatory message. Invalid or unavailable evidence returns a structured client/server error without secrets.

## Compliance

**GET `/api/compliance/audit/{standard}`** — prototype evidence-gap assessment.

Example: `GET /api/compliance/audit/OISD-118`

The response includes assessment status, supported controls, gaps, critical gaps, evidence records, corrective actions, methodology version, dataset hash, analysis ID, and limitations. Unknown standards return `status: "no_data"`. Results are decision support, not legal certification.

## Failure patterns

**GET `/api/patterns`** — deterministic aggregation across synthetic work orders and recovered incident records.

The response includes recurring patterns, affected equipment, counts, dates, supporting evidence IDs, graph statistics, methodology identity, and limitations. Relationships are investigation signals and do not establish causality.

## Documents

**POST `/api/documents/upload`** — upload one PDF or DOCX multipart `file`. Validates extension/signature, enforces the configured size limit, hashes content, extracts and chunks text, indexes chunks, and records the document. Duplicate content returns HTTP 409. Corrupt, unsupported, empty, or oversized uploads return structured 4xx errors.

**GET `/api/documents/stats`** — returns backend document inventory and index statistics. An empty corpus is a valid state.

## Copilot

**POST `/api/query`** — route a natural-language query. Representative request:

```json
{"query":"What evidence is available for confined-space entry requirements?","query_type":"knowledge"}
```

Knowledge responses expose answer/status, citations, confidence, and follow-up suggestions. Missing relevant evidence returns a no-evidence response. Gemini unavailability is reported explicitly; specialist analytics remain deterministic.

## Limitations

Schemas evolve through documented API contracts. Consult [API_CONTRACTS.md](API_CONTRACTS.md) and live OpenAPI documentation for exact fields. Do not send credentials in query bodies or URLs.
