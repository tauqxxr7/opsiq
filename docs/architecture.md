
# OPSIQ Architecture

```text
User / Field Technician
        │
React 18 + Vite + Tailwind
        │
FastAPI REST API
        │
LangGraph StateGraph Router
   ┌────┼──────────┬──────────┐
Expert Maintenance Compliance Pattern
   │        │          │          │
Dense + BM25 (RRF)  Clause map  NetworkX
   │
Cross-encoder reranking → Gemini 1.5 Flash → citations
```

Document ingestion preserves page and section metadata, chunks on sentence boundaries at roughly 400 tokens with overlap, and writes each chunk into both ChromaDB and the BM25 corpus. Retrieval fuses rankings with reciprocal rank fusion, reranks the top 20 pairs with `ms-marco-MiniLM-L-6-v2`, and exposes only the top five to synthesis.

The router uses an explicit `OpsIQState` and conditional LangGraph edges. Every terminal agent returns a structured response. The Copilot refuses synthesis when retrieval returns no evidence.
