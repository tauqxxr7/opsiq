# OPSIQ

### Evidence-grounded industrial intelligence for maintenance, compliance, failure-pattern analysis, and engineering knowledge retrieval.

OPSIQ combines grounded document retrieval with deterministic, traceable analytics over work orders, inspections, incidents, and uploaded technical documents.

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/tauqxxr7/opsiq/ci.yml?branch=main&style=flat-square&label=CI" alt="CI">
  <img src="https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React_18-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React 18">
  <img src="https://img.shields.io/badge/Vite_5-646CFF?style=flat-square&logo=vite&logoColor=white" alt="Vite 5">
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" alt="MIT license">
  <img src="https://img.shields.io/badge/Frontend-Vercel-000000?style=flat-square&logo=vercel" alt="Vercel">
  <img src="https://img.shields.io/badge/Backend-Railway-0B0D0E?style=flat-square&logo=railway" alt="Railway">
</p>

**[Live application](https://opsiq-one.vercel.app)** · **[API documentation](https://opsiq-production-b20c.up.railway.app/docs)** · **[Architecture](docs/architecture.md)** · **[Methodology](docs/METHODOLOGY.md)** · **[Data provenance](docs/data-provenance.md)**

<!-- Add the verified public demo-video URL here after upload. -->

## Product tour

| Operational overview | Maintenance evidence | Compliance gaps |
|---|---|---|
| ![OPSIQ dashboard](docs/screenshots/dashboard-desktop.png) | ![P-201 recurrence-risk analysis](docs/screenshots/maintenance-desktop.png) | ![OISD-118 evidence-gap assessment](docs/screenshots/compliance-desktop.png) |

See the [complete screenshot gallery](docs/screenshots/README.md).

## The problem

Industrial evidence is often distributed across work orders, inspections, incident records, manuals, and standards. Finding and connecting it can require several tools and manual cross-referencing. OPSIQ demonstrates a single evidence layer for retrieval and reproducible specialist analysis.

## What OPSIQ does

- **Expert Copilot:** grounded document retrieval with citations and explicit no-evidence behavior.
- **Maintenance Intelligence:** deterministic recurrence-risk scoring from work-order history.
- **Compliance Audit:** prototype evidence-gap assessment over synthetic OISD-118 inspection evidence.
- **Failure Patterns:** cross-source investigation signals derived from work orders and incidents.
- **Document Library:** validated PDF/DOCX ingestion, SHA-256 duplicate detection, chunking, indexing, and persistent inventory.
- **Traceability:** evidence IDs, dataset hashes, methodology versions, analysis IDs, limitations, and component calculations.

## How it works

```text
React / Vite
    │ REST
    ▼
FastAPI ── LangGraph query router
    ├── Expert Copilot ── dense + BM25 retrieval ── cross-encoder ── optional Gemini
    ├── Maintenance Agent ── deterministic six-component score
    ├── Compliance Agent ── record-derived OISD-118 gap matrix
    └── Pattern Agent ── work orders + incidents ── NetworkX evidence graph
           └── ChromaDB persistence + versioned methodology + SHA-256 identity
```

### Deterministic versus generative responsibilities

| Responsibility | Approach |
|---|---|
| Maintenance score | Deterministic formula over work-order evidence |
| Compliance status | Deterministic mapping over inspection records |
| Failure patterns | Deterministic aggregation and graph construction |
| Document retrieval | Dense and BM25 retrieval with reranking |
| Natural-language synthesis | Optional Gemini generation from retrieved context |
| Missing evidence | Explicit refusal or `status: no_data` |

Gemini never creates specialist scores. If relevant chunks are absent, the Copilot returns a no-evidence response.

## Evidence traceability

Each specialist analysis identifies its input dataset, evidence records, methodology version, and deterministic analysis identity. Unknown equipment and standards return `status: no_data` rather than being presented as low risk or compliant.

| Dataset | Records | Scope |
|---|---:|---|
| Work orders | 50 | Synthetic maintenance records across 15 equipment IDs |
| Inspection reports | 6 | Synthetic OISD-118 evidence |
| Incident history | 11 | Valid records recovered from a preserved corrupt artifact |

See [methodology](docs/METHODOLOGY.md) and [data provenance](docs/data-provenance.md).

## Verified results

Backend tests cover endpoints, analytics, ingestion, corruption handling, and traceability. An offline authenticity evaluation covers known and unknown queries. Frontend CI validates deployment configuration, linting, and production build. The public application and all seven routes have been smoke-tested against the deployed API.

These checks are regression evidence for the prototype—not a claim of real-world model accuracy.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite 5, Tailwind CSS, Recharts |
| Backend | FastAPI, Python 3.11, Uvicorn |
| Orchestration | LangGraph |
| Retrieval | ChromaDB, sentence-transformers, BM25Okapi, CrossEncoder |
| Optional synthesis | Google Gemini |
| Evidence graph | NetworkX |
| Processing | PyMuPDF, python-docx |
| Deployment | Vercel frontend, Railway backend |

## Repository structure

```text
backend/        agents, API, evidence schemas, services, tests, evaluation
frontend/       seven lazy-loaded routes and reusable UI components
docs/           architecture, methodology, contracts, provenance, submission assets
demo/           timed demonstration script
```

## Local setup

Prerequisites: Python 3.11 and Node.js 20+.

```bash
git clone https://github.com/tauqxxr7/opsiq.git
cd opsiq/backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp ../.env.example .env
python -m uvicorn main:app --reload --port 8000
```

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. First retrieval initialization may download embedding and reranker models.

## Environment variables

| Variable | Required | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | Copilot synthesis only | Server-side Gemini credential |
| `CHROMA_DB_PATH` | No | ChromaDB and ingestion-manifest path |
| `CORS_ORIGINS` | Production | Comma-separated frontend origins |
| `MAX_UPLOAD_SIZE_MB` | No | Upload cap; defaults to 20 |
| `VITE_API_URL` | Frontend production | Absolute backend API URL including `/api` |

Never commit `.env` files or API keys.

## API reference

Use the [deployed OpenAPI UI](https://opsiq-production-b20c.up.railway.app/docs), repository [API reference](docs/api_reference.md), and [API contracts](docs/API_CONTRACTS.md).

## Testing and CI

```bash
cd backend
python -m pytest -q
python -m compileall -q .
python evaluation/run_evaluation.py

cd ../frontend
npm ci
npm run lint
npm run check:deployment
npm run build
```

## Responsible-use limitations

- All bundled operational records are synthetic demonstration data.
- Compliance covers only bundled OISD-118 evidence and is not legal certification.
- Maintenance scores summarize historical recurrence evidence and do not predict a component or failure date.
- Pattern relationships are investigation signals and do not establish causality.
- Retrieval quality depends on uploaded document quality and coverage.
- The prototype has no authentication, tenancy, or plant-system integration.
- Safety, maintenance, and compliance decisions require authorized human review.

## What OPSIQ does not claim

OPSIQ does not claim real-time sensor monitoring, exact failure prediction, legal certification, causal diagnosis, guaranteed hallucination prevention, enterprise security certification, or validated financial savings.

## Future roadmap

Controlled plant-data validation; authentication and tenant isolation; object storage and asynchronous ingestion; retrieval and load testing; human approval and audit workflows; enterprise connectors; and security hardening.

## Documentation

Start with the [documentation index](docs/README.md).

## License

Released under the [MIT License](LICENSE).

## Author

Built by [Tauqeer Bharde](https://github.com/tauqxxr7) for ET AI Hackathon 2.0, Problem Statement #8.
