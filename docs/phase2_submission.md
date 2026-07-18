
# OPSIQ — AI-Powered Industrial Knowledge Intelligence Platform
## ET AI Hackathon 2.0 · Phase 2 Submission · Problem Statement #8

## 1. Executive Summary

OPSIQ is the evidence layer for asset-intensive operations. It converts fragmented manuals, standards, work orders, inspections and incident reports into cited answers, predictive maintenance signals, audit-ready compliance mappings and proactive failure warnings. It is delivered as a production-shaped React/FastAPI application with four specialised agents orchestrated through LangGraph.

The platform’s operating principle is strict: no retrieved evidence, no generated answer. That boundary makes OPSIQ appropriate for safety-critical workflows where fluent but unsupported text is unacceptable.

## 2. Problem Definition and Evidence

Industrial organisations possess the information needed to prevent many failures, yet cannot retrieve and connect it at the point of work. The source brief cites McKinsey’s estimate that professionals spend 35% of working time searching for information and notes that Indian plants commonly operate across 7–12 disconnected systems. The result is repeated diagnosis, slow permit checks, loss of retiring-engineer knowledge and preventable downtime.

The challenge has four linked dimensions:

1. Knowledge retrieval fails across inconsistent formats and terminology.
2. Maintenance history is reviewed as isolated work orders rather than a failure trajectory.
3. Compliance evidence is assembled reactively before audits.
4. Similar incidents across assets and time are rarely correlated.

OPSIQ addresses all four through one indexed, permission-ready intelligence layer.

## 3. Product Solution

The Expert Copilot answers operational questions from documents and exposes the precise source page. Maintenance Intelligence combines work-order recurrence and precursor symptoms to rank asset risk and produce structured RCA evidence. Compliance Audit maps regulatory clauses to current procedural evidence and identifies missing or expired controls. The Failure Pattern Engine constructs equipment–failure–cause relationships to surface recurring paths.

Primary users are field technicians, reliability engineers, maintenance planners, safety and compliance officers, plant managers and knowledge administrators.

## 4. System Architecture

```text
Responsive React 18 interface
        │ HTTPS / REST
FastAPI validation and upload boundary
        │
LangGraph StateGraph query router
 ┌──────┼────────────┬─────────────┐
Expert  Maintenance  Compliance    Pattern
Copilot Agent        Agent         Engine
 │         │             │            │
 └── ChromaDB + BM25 ────┘        NetworkX
             │
     Cross-encoder reranker
             │
      Gemini 1.5 Flash
             │
 Answer + citations + confidence
```

Documents enter through a bounded multipart endpoint. PyMuPDF or python-docx extracts content while preserving document, page, section and type metadata. Sentence-aware chunks are dual-indexed in ChromaDB and BM25. At query time, reciprocal rank fusion merges dense and sparse results; a cross-encoder reranks the best candidates before Gemini sees them.

## 5. Four-Agent Design Rationale

### Expert Knowledge Copilot

Industrial queries mix semantic intent with exact identifiers. Dense retrieval understands “safe entry into enclosed equipment,” while BM25 reliably finds “OISD-118 Clause 4.3.2” and “P-201.” RRF prevents either method from dominating. Cross-encoder scoring then evaluates query–passage pairs jointly. Citations carry document, page, section, excerpt and relevance.

### Maintenance Intelligence

The maintenance agent operates on a unified equipment timeline. It groups historical work orders, precursor symptoms, actions and downtime. P-201 deliberately contains four bearing/seal events in 18 months, allowing the demo to expose a genuine recurrence rather than a hardcoded claim. Its output is structured for planner review: risk, component, failure window and matching records.

### Compliance Audit

Regulatory obligations are clause-addressable records. Semantic matching is required because plant procedures often paraphrase standards. The matrix distinguishes compliant evidence, ordinary gaps and critical gaps; every row identifies its evidence record. Evidence-package generation is designed as a downstream controlled export.

### Failure Pattern Engine

NetworkX models Equipment → Failure Mode → Root Cause paths. Repeated subgraphs reveal systemic relationships that chronological incident review misses. The engine returns counts and risk classification so teams can intervene before the next recurrence.

## 6. RAG Pipeline Technical Deep Dive

### Ingestion

PDF and DOCX inputs are routed by format. Page text and heading-like sections are extracted. Chunking occurs at sentence boundaries, targets approximately 400 tokens and retains the prior two sentences as overlap. Tiny fragments are rejected. Each chunk receives a deterministic ID and metadata.

### Indexing

The dense path uses `all-MiniLM-L6-v2` embeddings in a cosine ChromaDB collection. The sparse path tokenises technical strings and builds BM25Okapi over the same corpus. Upsert semantics prevent duplicate chunk IDs.

### Retrieval and reranking

The system retrieves up to 20 results per path. RRF combines rank positions using `1 / (60 + rank)`, which is robust to incomparable raw score scales. The `ms-marco-MiniLM-L-6-v2` cross-encoder scores candidate pairs; only the best five become model context.

### Synthesis and integrity

Gemini receives an explicit evidence envelope with numbered passages. The prompt requires claims to cite those numbers. If retrieval is empty, the model is never called and OPSIQ returns “Insufficient documentation found.” Confidence is derived from the top reranking scores, not invented by the language model.

## 7. Demonstration and Validation

The four-minute flow validates the entire system: real upload and indexing, grounded Copilot response with clickable passages, P-201 recurrence analysis from 50 synthetic work orders, an OISD-118 compliance matrix backed by inspection records, and an interactive architecture view.

Acceptance checks include frontend production build, Python compilation, JSON schema/count checks, secret scanning, responsive navigation, API timeouts and verification that no generic response bypasses retrieval.

## 8. Business Impact and ROI

Using the source brief’s 35% search-time baseline, reducing search to 5% recovers 30 percentage points. For 200 engineers at an average ₹8 lakh annual CTC, the gross recovered-capacity value is approximately ₹4.8 crore annually before adoption discount; a conservative realised value remains around ₹4.2 crore.

The brief cites ₹2,800 crore of annual unplanned-downtime exposure in Indian heavy industry and a 20–30% predictive-maintenance reduction range. For a mid-sized refinery, the stated conservative opportunity is ₹18–25 crore annually. Compliance value is asymmetric: avoiding one shutdown day can protect ₹5–15 crore, in addition to statutory penalties and safety exposure.

Commercial tiers are Starter at ₹2.5 lakh/month, Professional at ₹8 lakh/month and custom Enterprise/on-premise. Five first-year plants imply ₹3–4 crore ARR; 80 plants support a ₹50+ crore year-three target.

## 9. Scalability, Security and Deployment Roadmap

**MVP:** single plant, local ChromaDB, 50,000 chunks and Railway deployment.

**Production (three months):** multi-tenancy, managed vector storage, PostgreSQL metadata, JWT/RBAC, Celery/Redis ingestion, 500,000+ chunks per tenant and 50 concurrent users per plant.

**Enterprise (12 months):** air-gapped deployment, domain-tuned embeddings, SAP PM / IBM Maximo integration, SCADA condition ingestion and a field-native mobile experience.

Security controls include AES-256 at rest, TLS in transit, tenant-scoped indexes, Field Technician / Engineer / Manager / Admin roles, immutable query and document-access audit logs, malware scanning and retention policies. Horizontal FastAPI and worker pools separate interactive latency from ingestion load.

## 10. Conclusion

OPSIQ turns industrial documentation from passive storage into an operational control surface. Its four-agent design maps directly to the daily decisions of technicians, reliability teams, compliance officers and plant leaders. Its hybrid retrieval and citation boundary make every answer inspectable. Its maintenance and graph layers convert history into foresight.

This is not a generic chatbot interface. It is a working foundation for industrial knowledge intelligence: grounded, traceable, deployable and engineered to scale from one plant to an air-gapped enterprise estate.

**Submitted by Tauqeer Sameer Bharde**  
ET AI Hackathon 2.0 · Phase 2 · Problem Statement #8  
Submission deadline: 22 July 2026, 11:59 PM IST
