
# OPSIQ Architecture

```text
User / Field Technician
        â”‚
React 18 + Vite + Tailwind
        â”‚
FastAPI REST API
        â”‚
LangGraph StateGraph Router
   â”Œâ”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
Expert Maintenance Compliance Pattern
   â”‚        â”‚          â”‚          â”‚
Dense + BM25 (RRF)  Clause map  NetworkX
   â”‚
Cross-encoder reranking â†’ Gemini 1.5 Flash â†’ citations
```

Document ingestion preserves page and section metadata, chunks on sentence boundaries at roughly 400 tokens with overlap, and writes each chunk into both ChromaDB and the BM25 corpus. Retrieval fuses rankings with reciprocal rank fusion, reranks the top 20 pairs with `ms-marco-MiniLM-L-6-v2`, and exposes only the top five to synthesis.

The router uses an explicit `OpsIQState` and conditional LangGraph edges. Every terminal agent returns a structured response. The Copilot refuses synthesis when retrieval returns no evidence.
