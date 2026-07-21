# OPSIQ — Phase 2 Submission

## 1. Executive summary

OPSIQ is a production-deployed prototype for grounded industrial document retrieval and reproducible specialist analytics. It combines a cited document Copilot with deterministic maintenance, compliance, and failure-pattern workflows. Every bundled operational record is synthetic.

## 2. Industrial problem

Industrial evidence is distributed across work orders, inspections, incidents, manuals, and standards. Engineers must often search and cross-reference these sources manually. OPSIQ demonstrates how one evidence layer can improve retrieval, maintenance-history review, compliance-gap triage, incident learning, and knowledge transfer.

## 3. Proposed solution

A React application calls a FastAPI service. LangGraph routes requests to four specialists: Expert Copilot, Maintenance Intelligence, Compliance Audit, and Failure Patterns. Generative synthesis is evidence-gated; specialist scores and findings are deterministic.

## 4. Target users

Reliability engineers, maintenance planners, field technicians, safety and compliance teams, plant managers, and knowledge administrators.

## 5. Verified capabilities

- cited retrieval over indexed PDF and DOCX content;
- deterministic recurrence-risk analysis over work orders;
- prototype OISD-118 evidence-gap assessment;
- cross-source work-order and incident pattern aggregation;
- upload validation, hashing, duplicate rejection, chunking, indexing, and persistent inventory;
- no-data behavior for unknown equipment and standards;
- evidence IDs, dataset hashes, methodology versions, and deterministic analysis IDs.

## 6. System architecture

```text
React/Vite → FastAPI → LangGraph router
  ├─ Copilot → dense + BM25 → cross-encoder → optional Gemini
  ├─ Maintenance → deterministic six-component score
  ├─ Compliance → inspection evidence matrix
  └─ Patterns → NetworkX evidence graph
                 ↓
       ChromaDB + persistent ingestion registry
```

## 7. Hybrid retrieval pipeline

PDF and DOCX text is validated, extracted, sentence-aware chunked, and indexed. Dense embeddings and BM25 retrieve complementary candidates. Reciprocal rank fusion combines rankings and a cross-encoder reranks the strongest passages. Gemini receives retrieved context only. Missing evidence produces a no-evidence response.

## 8. Deterministic maintenance methodology

Maintenance scores summarize historical recurrence evidence using dominant-failure recurrence, recent incidents, ordinal severity, downtime burden, repeated dominant root cause, and interval trend. The API exposes score components, supporting work orders, recurrence intervals, methodology version, and limitations. It does not predict a failure date.

## 9. Compliance evidence-gap methodology

The compliance agent evaluates six bundled synthetic OISD-118 inspection records. It returns supported controls, gaps, critical gaps, evidence IDs, corrective actions, and a reproducible analysis identity. This is prototype decision support, not legal certification.

## 10. Failure-pattern analysis

The pattern agent combines work orders and recovered incident records in a NetworkX graph. It reports recurring equipment/failure relationships, shared root causes, downtime clusters, dates, and supporting record IDs. Outputs are investigation signals, not causal conclusions.

## 11. Copilot grounding and refusal behavior

The Copilot is retrieval-first. If no relevant chunks exist, it does not call the language model. When Gemini credentials are absent, the system reports synthesis unavailability instead of hiding the condition. Citations identify retrieved source material.

## 12. Evidence provenance

Datasets are hashed and specialist responses identify their evidence. The original corrupt incident artifact is preserved as a test fixture; only independently valid records before the corruption boundary are recovered. See [data provenance](data-provenance.md).

## 13. Synthetic data disclosure

The repository contains 50 synthetic work orders, six synthetic OISD-118 inspection records, and 11 recovered synthetic incident records. No result should be interpreted as a claim about a real plant.

## 14. Validation results

The project includes backend tests, Python source compilation, an authenticity evaluation, frontend linting, deployment checks, and a production build. CI is green and public routes have been smoke-tested. This is regression evidence, not external accuracy validation.

## 15. Deployment architecture

Vercel hosts the React frontend. Railway builds the Python 3.11 FastAPI container, checks `/health`, and uses persistent storage for ChromaDB and the ingestion registry. Gemini credentials remain server-side.

## 16. Current limitations

Synthetic evidence only; narrow OISD-118 scope; no authentication or tenancy; no plant-system connectors; small evaluation corpus; retrieval quality depends on document coverage; and safety decisions require human review.

## 17. Future roadmap

Controlled plant-data validation, authentication and tenant isolation, asynchronous ingestion, object storage, retrieval evaluation, observability, human approval workflows, security hardening, and enterprise connectors.

## 18. Live links

- [Application](https://opsiq-one.vercel.app)
- [API documentation](https://opsiq-production-b20c.up.railway.app/docs)
- [Repository](https://github.com/tauqxxr7/opsiq)
