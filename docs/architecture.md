# OPSIQ Architecture

```text
User / Field Technician
        |
React 18 + Vite + Tailwind
        |
FastAPI REST API
        |
LangGraph StateGraph Router
   +----+-----------+-----------+
Copilot Maintenance Compliance Pattern
   |        |           |          |
Hybrid RAG Weighted risk Evidence   Cross-source aggregation
   |                    matrix      + knowledge graph
Dense + BM25 (RRF)
   |
Cross-encoder reranking -> Gemini synthesis -> citations
```

## Evidence flow

Document ingestion preserves page and section metadata, chunks on sentence boundaries at roughly 400 tokens with overlap, and writes each chunk into ChromaDB and the BM25 corpus. Retrieval fuses rankings with reciprocal rank fusion, reranks the top candidates, and exposes only selected evidence to synthesis. Copilot refuses to answer when retrieval returns no chunks.

The deterministic analytics path does not require Gemini. Maintenance reads work orders and calculates an inspectable weighted score. Compliance maps every matching inspection record without fixed totals. Pattern analysis normalizes work orders and incident records, groups recurring relationships, and emits record IDs on every aggregate. The in-process knowledge graph uses typed equipment, failure-mode, and root-cause nodes with weighted evidence edges.

`incident_history.json` currently contains 11 valid records followed by malformed content. A tolerant read-only loader recovers only independently valid JSON objects; it does not repair, replace, or infer missing records. Source counts expose that limitation to API consumers.

The router uses explicit state and conditional LangGraph edges. Analytics responses label the bundled dataset as synthetic and separate evidence sufficiency from predictive certainty.
