
# OPSIQ
> AI-powered Industrial Knowledge Intelligence Platform

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![LangGraph](https://img.shields.io/badge/LangGraph-FF6B35?style=flat)
![ChromaDB](https://img.shields.io/badge/ChromaDB-orange?style=flat)
![Gemini](https://img.shields.io/badge/Gemini_1.5_Flash-4285F4?style=flat&logo=google&logoColor=white)

## The problem

Professionals in asset-intensive industries spend **35% of working hours** searching for information already present in organisational systems. A typical plant spans 7–12 disconnected document systems; that fragmentation contributes to compliance failures, repeated incidents and avoidable downtime.

## The solution

OPSIQ turns industrial documents into a continuously updated, evidence-grounded intelligence layer. Four LangGraph-routed agents serve operational questions, maintenance prediction, compliance auditing and cross-document pattern discovery.

- **Expert Knowledge Copilot** — dense + BM25 retrieval, cross-encoder reranking, source citations
- **Maintenance Intelligence** — equipment history, predictive signatures and structured RCA
- **Compliance Audit** — clause-to-procedure gap detection and evidence mapping
- **Failure Pattern Engine** — NetworkX-powered recurrence detection

## Architecture

React → FastAPI → LangGraph router → specialised agent → ChromaDB/BM25/NetworkX → Gemini synthesis → cited response.

Read the [architecture deep dive](docs/architecture.md), [API reference](docs/api_reference.md), and [Phase 2 submission](docs/phase2_submission.md).

## Quick start

```bash
git clone https://github.com/tauqxxr7/opsiq
cd opsiq

cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
uvicorn main:app --reload

# New terminal
cd frontend
npm install
npm run dev
```

Set `GEMINI_API_KEY` in `backend/.env`. Open http://localhost:5173. API docs are at http://localhost:8000/docs.

## Safety contract

OPSIQ never synthesises an answer without retrieved evidence. Empty retrieval returns “Insufficient documentation found.” API keys remain in environment files. Uploads are deleted after indexing, requests have bounded client timeouts, and every generated knowledge answer carries source metadata.

## Built for

**ET AI Hackathon 2.0** · Phase 2 · Problem Statement #8  
Tauqeer Sameer Bharde · [github.com/tauqxxr7](https://github.com/tauqxxr7)
