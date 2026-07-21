# OPSIQ

### Traceable Industrial Knowledge Intelligence

> ET AI Hackathon 2.0 · Problem Statement #8 · authenticity-hardened prototype

<p align="center">
  <img src="https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangGraph-FF6B35?style=flat-square" alt="LangGraph">
  <img src="https://img.shields.io/badge/React_18-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React 18">
  <img src="https://img.shields.io/badge/Evidence-Traceable-22C55E?style=flat-square" alt="Evidence traceable">
</p>

**[Live platform](https://opsiq-one.vercel.app)** · **[API docs](https://opsiq-production-b20c.up.railway.app/docs)** · **[Methodology](docs/METHODOLOGY.md)** · **[API contracts](docs/API_CONTRACTS.md)**

> The live deployment may trail this feature branch until it is reviewed and deployed. No deployment is performed by this sprint.

## What OPSIQ demonstrates

OPSIQ is a multi-agent prototype for querying and analysing industrial evidence. It combines a document copilot with three deterministic specialist analyses:

- maintenance recurrence-risk scoring from work orders;
- OISD-118 prototype evidence-gap assessment from inspection records;
- cross-source failure-pattern aggregation from work orders and incident history.

The specialist outputs are not opaque predictions. Each successful analysis carries the exact evidence IDs, dataset hash, methodology version, deterministic analysis ID, limitations and component-level calculations. Valid queries with no matching evidence return `status: no_data`; they are never presented as low risk or compliant.

## Architecture

```text
React / Vite
    │
    ▼
FastAPI ── LangGraph query router
    ├── Expert Copilot ── hybrid retrieval ── optional Gemini synthesis
    ├── Maintenance Agent ── deterministic six-component score
    ├── Compliance Agent ── record-derived OISD-118 gap matrix
    └── Pattern Agent ── work orders + incidents ── NetworkX evidence graph
           │
           ├── ChromaDB + sentence-transformers + BM25 + cross-encoder
           └── versioned methodology + SHA-256 evidence identity
```

The copilot refuses when no relevant chunks are available. If chunks exist but `GEMINI_API_KEY` is absent, it returns citations and an explicit synthesis-unavailable message rather than silently generating content.

## Evidence shipped with the prototype

| Dataset | Runtime records | Scope |
|---|---:|---|
| Work orders | 50 | Synthetic maintenance records across 15 equipment IDs |
| Inspection reports | 6 | Synthetic OISD-118 evidence only: 2 compliant, 3 gaps, 1 critical |
| Incident history | 11 | Independently valid records recovered from the original corrupt artifact |

The original incident artifact is preserved for audit testing. Its SHA-256, corrupt region and recovery boundary are documented in [data provenance](docs/data-provenance.md). No damaged record was inferred or regenerated.

## Deterministic maintenance score

| Signal | Weight |
|---|---:|
| Dominant failure recurrence | 25% |
| Recent incidents in exclusive age buckets | 20% |
| Mean ordinal severity | 20% |
| Mean downtime against dataset P90 | 15% |
| Repeated dominant root cause | 10% |
| Shrinking observed intervals | 10% |

See [the complete formulas and thresholds](docs/METHODOLOGY.md). The result is historical recurrence-risk analytics—not a trained predictive-maintenance model—and it does not output a future failure date.

## Document ingestion

PDF and DOCX uploads are streamed with a configurable size limit, checked for extension/signature mismatch, parsed for text, chunked at sentence boundaries, indexed, and registered in a persistent manifest. SHA-256 duplicate detection returns HTTP 409. The document library displays only the backend inventory; no sample documents are represented as indexed unless they actually are.

Chunking targets approximately 400 words and carries the final two sentences into the next chunk. Dense and BM25 candidates are fused, then reranked by `cross-encoder/ms-marco-MiniLM-L-6-v2` when the retrieval service initializes. First initialization can download local embedding and reranker models.

## Quick start

```bash
git clone https://github.com/tauqxxr7/opsiq.git
cd opsiq

cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp ../.env.example .env
python -m uvicorn main:app --reload --port 8000
```

```bash
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. A Gemini key is optional for health checks and deterministic specialist agents; it is required only for copilot synthesis after retrieval.

## Verification

```bash
cd backend
python -m pytest -q
python -m compileall -q .
python evaluation/run_evaluation.py

cd ../frontend
npm ci
npm run lint
npm run build
```

The offline evaluation covers known and unknown specialist queries, deterministic traceability, cross-source pattern inputs, copilot refusal, and citation-field completeness. It is a small regression suite, not a claim of real-world model accuracy.

## Environment

| Variable | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | Copilot synthesis only | Gemini API credential; backend environment only |
| `CHROMA_DB_PATH` | No | Persistent vector database and ingestion manifest path |
| `CORS_ORIGINS` | Production | Comma-separated frontend origins |
| `MAX_UPLOAD_SIZE_MB` | No | Upload cap; default 20 |
| `VITE_API_URL` | Frontend production | Backend origin; frontend adds `/api` |

Never commit `.env` or API keys. Railway needs a volume mounted for `CHROMA_DB_PATH`; otherwise indexed uploads are ephemeral.

## Limitations and responsible use

- Every bundled operational record is synthetic demonstration data.
- Compliance covers only the six bundled OISD-118 rows and is not legal certification. Factory Act, DGMS and PESO are roadmap integrations, not current evidence claims.
- Maintenance scores describe historical recurrence risk; they do not predict a component or failure date.
- Pattern relationships are correlations and do not establish causality.
- Retrieval quality depends on uploaded document quality and coverage.
- There is no authentication or plant tenancy in this prototype.
- The evaluation corpus is intentionally small and deterministic; external validation is still required.

## Project map

```text
backend/
  agents/       specialist and copilot agents
  api/          FastAPI routes and upload contracts
  core/         configuration, state, evidence schemas, methodology versions
  data/         synthetic runtime evidence
  evaluation/   offline authenticity regression suite
  services/     processing, retrieval, registry, evidence graph
  tests/        endpoint, analytics, ingestion and corruption tests
frontend/src/
  pages/        seven lazy-loaded application routes
  components/   reusable interface and charts
docs/           methodology, API contracts and data provenance
.github/         CI and repository metadata
```

## License and author

Built by [Tauqeer Sameer Bharde](https://github.com/tauqxxr7) for ET AI Hackathon 2.0. Review the repository license before reuse.
