# OPSIQ — 3 minute 40 second demonstration

Record at 1440×900 or 1080p, browser zoom 100%. Hide credentials and unrelated tabs. Move the cursor slowly and pause over evidence IDs.

| Time | Route and exact interaction | Narration |
|---|---|---|
| 0:00–0:25 | Open `/`. Point to the evidence-derived metrics and latest-evidence feed. | “Industrial evidence is often distributed across work orders, inspections, incidents, and technical documents. OPSIQ makes that evidence queryable and supports reproducible specialist analysis.” |
| 0:25–0:45 | Click **Maintenance**. Wait for P-201 to load. | “OPSIQ combines grounded retrieval with deterministic maintenance, compliance, and pattern analysis. Every specialist result exposes supporting records.” |
| 0:45–1:20 | On `/maintenance`, select P-201 if needed. Pause on the score, six components, and work-order table. | “For pump P-201, OPSIQ calculates historical recurrence risk from documented evidence such as recurrence, recency, severity, downtime, repeated root causes, and interval trends. This is not a predicted failure date.” |
| 1:20–1:52 | Click **Compliance**. Keep OISD-118 selected. Point to one supported control and the hot-work-permit gap. | “The compliance view performs a prototype evidence-gap assessment. It is decision support, not legal certification.” |
| 1:52–2:20 | Click **Failure patterns**. Pause over one pattern and its evidence IDs. | “The graph correlates work orders and incident records. These outputs are investigation signals derived from supporting records, not causal conclusions.” |
| 2:20–2:48 | Click **Copilot**. Suggested prompt: “What evidence is available for confined-space entry requirements?” Point to citation and confidence areas. | “Hybrid dense and BM25 retrieval is reranked before optional Gemini synthesis. When relevant evidence is unavailable, OPSIQ returns a no-evidence response instead of inventing an answer.” |
| 2:48–3:05 | Click **Document library**. Point to the PDF/DOCX upload boundary and backend inventory. | “Uploads are validated, hashed for duplicate detection, chunked, indexed, and recorded in a persistent manifest. Only actually indexed documents appear here.” |
| 3:05–3:30 | Click **Architecture**. Trace one left-to-right path without circling the screen. | “FastAPI defines the API boundary, LangGraph routes requests, ChromaDB and BM25 support retrieval, and versioned methodology plus SHA-256 identities make results traceable.” |
| 3:30–3:40 | Return to `/`. | “OPSIQ is a production-deployed prototype using synthetic demonstration data. Next steps are controlled plant validation, authentication, tenancy, and enterprise connectors.” |

## Slow-response fallback

If an upload or Gemini response is slow, do not wait. State: “Ingestion and model synthesis are network- and model-dependent; the deterministic specialist routes remain available.” Continue to the next route. Never substitute mock output.
