# OPSIQ
### Industrial Knowledge Intelligence Platform
> Built for ET AI Hackathon 2.0 · Problem Statement #8 · 60,977 participants

<p align="center">
  <img src="https://img.shields.io/badge/Python_3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangGraph-FF6B35?style=flat-square" alt="LangGraph">
  <img src="https://img.shields.io/badge/ChromaDB-orange?style=flat-square" alt="ChromaDB">
  <img src="https://img.shields.io/badge/React_18-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React 18">
  <img src="https://img.shields.io/badge/Gemini_1.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white" alt="Gemini 1.5 Flash">
  <img src="https://img.shields.io/badge/Railway-0B0D0E?style=flat-square&logo=railway&logoColor=white" alt="Railway">
  <img src="https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white" alt="Vercel">
</p>

<p align="center">
  <strong><a href="https://opsiq-one.vercel.app">→ Live Platform</a></strong> ·
  <strong><a href="https://opsiq-production-b20c.up.railway.app/docs">→ API Docs</a></strong> ·
  <strong><a href="#">→ Demo Video</a></strong> ← placeholder, I will fill this
</p>

---

## The Problem

India's industrial sector operates across 7–12 disconnected document systems per plant. Professionals spend **35% of their working hours** searching for information that already exists somewhere in their organisation — maintenance manuals in one place, inspection records in another, safety procedures in a third.

When an engineer needs the confined space entry procedure before entering Tank C-7, they shouldn't need to call three people and wait 20 minutes. When Pump P-201 trips for the fourth time this year, the root cause shouldn't require manually cross-referencing four years of work orders.

> A 2024 McKinsey survey found that asset-intensive industry professionals lose 35% of working hours to document search. A NASSCOM-EY study found the average Indian industrial plant operates across 7–12 disconnected systems. An estimated 25% of experienced industrial engineers will retire by 2030, taking decades of undocumented knowledge with them. Once gone, it cannot be recovered.

---

## The Solution

OPSIQ is a multi-agent AI platform that ingests your existing industrial documents and makes their collective intelligence queryable, actionable, and continuously updated — at the point of need, on any device.

It does not replace your document systems. It sits on top of them and makes everything inside them instantly accessible through natural language.

---

## Architecture

```text
User Query
    │
    ▼
FastAPI Router → Query Classifier
    │
    ├──► Expert Copilot Agent
    │    Hybrid RAG (Dense + BM25) → Cross-encoder
    │    reranking → Gemini synthesis →
    │    Citation packaging
    │
    ├──► Maintenance Intelligence Agent
    │    Work order analysis → Deterministic risk
    │    scoring (6-component weighted formula) →
    │    Evidence-grounded RCA generation
    │
    ├──► Compliance Audit Agent
    │    OISD/Factory Act requirement mapping →
    │    Inspection record cross-reference →
    │    Gap identification → Evidence packages
    │
    └──► Failure Pattern Engine
         Cross-document incident correlation →
         NetworkX graph analysis → Systemic
         pattern detection → Proactive warnings
    │
    ▼
ChromaDB (Vector Store)
BM25Okapi (Keyword Index)
NetworkX (Knowledge Graph)
```

---

## Four Agents, One Platform

### Expert Knowledge Copilot

RAG-powered conversational AI over your document corpus. Every response cites the source document, page number, and section. Confidence-scored. Zero hallucination policy — if retrieval confidence falls below threshold, the system says so rather than inventing an answer.

### Maintenance Intelligence Agent

Deterministic risk scoring from work order evidence. Six-component weighted formula: recurrence frequency (25%), recent incidents (20%), severity (20%), downtime burden (15%), repeated root cause (10%), shrinking failure intervals (10%). Every risk score returns a full breakdown object — no black box, no hardcoded outputs.

### Compliance Audit Agent

Maps current procedures against OISD, Factory Act, DGMS, and PESO standards. Derives compliance percentage from actual inspection records. Returns prioritised corrective action list with evidence sources. Explicitly labelled as prototype evidence-gap assessment, not legal certification.

### Failure Pattern Engine

Cross-document incident correlation using NetworkX. Identifies recurring equipment/failure-mode combinations, shared root causes across multiple assets, high-downtime clusters, and repeated precursor symptoms. Returns first-seen, last-seen, recurrence count, and supporting record IDs.

---

## RAG Pipeline

```text
Document Upload (PDF/DOCX/JSON)
    │
    ▼
Semantic Chunking
(sentence-boundary aware, 400-token target,
50-token overlap, section headers preserved)
    │
    ▼
Dual Indexing
├── Dense: sentence-transformers → ChromaDB
└── Sparse: BM25Okapi keyword index
    │
    ▼
Hybrid Retrieval (top-20 candidates)
    │
    ▼
Cross-encoder Reranking (ms-marco-MiniLM-L-6-v2)
    │
    ▼
Confidence Scoring
(below 0.30 → return "insufficient documentation"
rather than hallucinate)
    │
    ▼
Gemini 1.5 Flash Synthesis
(strict context-only, citation-mandatory)
    │
    ▼
Response + Citations + Confidence Score
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS |
| Backend | FastAPI, Python 3.11, uvicorn |
| Orchestration | LangGraph (multi-agent StateGraph) |
| LLM | Google Gemini 1.5 Flash |
| Vector Store | ChromaDB (cosine similarity) |
| Keyword Search | BM25Okapi (rank-bm25) |
| Reranking | CrossEncoder (ms-marco-MiniLM-L-6-v2) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Knowledge Graph | NetworkX + Pyvis |
| Document Processing | PyMuPDF, python-docx, unstructured |
| Backend Deploy | Railway (Docker, Python 3.11-slim) |
| Frontend Deploy | Vercel (SPA routing) |

---

## Quick Start

```bash
# Clone
git clone https://github.com/tauqxxr7/opsiq
cd opsiq

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
# Add your GEMINI_API_KEY to .env
uvicorn main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```

Get a free Gemini API key at **[aistudio.google.com](https://aistudio.google.com)**.

---

## Project Structure

```text
opsiq/
├── backend/
│   ├── agents/              # Four specialised AI agents
│   ├── services/            # RAG pipeline, retrieval,
│   │                        # embedding, knowledge graph
│   ├── api/                 # FastAPI route handlers
│   ├── core/                # LangGraph orchestrator,
│   │                        # state schema, config
│   └── data/
│       └── synthetic/       # 50 work orders, inspection
│                            # reports, incident history
├── frontend/
│   └── src/
│       ├── pages/           # 7 application pages
│       └── components/      # Reusable UI components
├── docs/                    # Architecture and API reference
├── demo/                    # Demo script and assets
└── DEPLOYMENT.md            # Railway + Vercel setup guide
```

---

## Limitations

- All operational records are **synthetic demonstration data**. Designed for realistic testing, not real plant operations.
- Maintenance output is **recurrence-risk analytics** derived from work order history. It is not a trained predictive-maintenance machine-learning model.
- Compliance output is a **prototype evidence-gap assessment**. It is not legal certification under OISD, Factory Act, DGMS, or PESO.
- LLM responses are grounded in indexed documents. Answer quality depends on documentation coverage.
- ChromaDB persistence requires a mounted volume in production. Ephemeral deployments lose indexed documents on restart.
- First request after cold start incurs model download latency (sentence-transformers).

---

## Judging Criteria Alignment

| Criterion | Weight | OPSIQ Approach |
|---|---:|---|
| Innovation | 25% | Hybrid RAG + 4-agent orchestration applied to Indian industrial context |
| Business Impact | 25% | Addresses ₹2,800 Cr unplanned downtime problem with quantified ROI |
| Technical Excellence | 20% | Deterministic risk scoring, cross-encoder reranking, evidence-gated synthesis |
| Scalability | 15% | Railway + Vercel deployment, ChromaDB volume persistence, horizontal-ready API |
| User Experience | 15% | 7-page React platform, mobile-responsive, real-time intelligence feed |

---

## Built By

**Tauqeer Sameer Bharde**<br>
B.Tech — Artificial Intelligence & Data Science<br>
SIES Graduate School of Technology, Navi Mumbai<br>
GitHub: [@tauqxxr7](https://github.com/tauqxxr7)

*ET AI Hackathon 2.0 | Phase 2 | Problem Statement #8*<br>
*60,977 registered participants*
