# OPSIQ

> AI-powered Industrial Knowledge Intelligence Platform

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![LangGraph](https://img.shields.io/badge/LangGraph-FF6B35?style=flat)
![ChromaDB](https://img.shields.io/badge/ChromaDB-orange?style=flat)
![Gemini](https://img.shields.io/badge/Gemini-4285F4?style=flat&logo=google&logoColor=white)

OPSIQ turns industrial manuals, standards, work orders, inspections, and incident reports into cited answers, maintenance signals, compliance evidence, and recurring-failure insights.

## Architecture

React 18 + Vite → FastAPI → LangGraph router → specialised agents → ChromaDB/BM25/NetworkX → Gemini synthesis → cited response.

Read the [architecture deep dive](docs/architecture.md), [API reference](docs/api_reference.md), and [Phase 2 submission](docs/phase2_submission.md).

## Environment variables

Copy `.env.example` to `backend/.env` for local backend development. Never commit `.env` files.

| Variable | Service | Required | Purpose |
| --- | --- | --- | --- |
| `GEMINI_API_KEY` | Backend | Optional for startup; required for Gemini synthesis | Read only from the process environment or an ignored local `.env` file. |
| `CHROMA_DB_PATH` | Backend | No | ChromaDB persistence directory. The backend default is `backend/data/chroma_db`; the example uses backend-local `./data/chroma_db`. |
| `CORS_ORIGINS` | Backend | Production | Comma-separated frontend origins. Local defaults include `http://localhost:5173` and `http://127.0.0.1:5173`. |
| `VITE_API_URL` | Frontend | Production build | Backend API base URL including `/api`. Local fallback is `http://localhost:8000/api`. |

Example frontend development file at `frontend/.env.local`:

```dotenv
VITE_API_URL=http://localhost:8000/api
```

Do not put API keys in `VITE_*` variables: Vite embeds them in browser assets.

## Local development

Backend, using Python 3.11:

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Verify liveness:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"operational","service":"OPSIQ"}
```

Frontend:

```bash
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. Use `npm install` only when intentionally updating dependencies and the lockfile.

## Docker backend

The Docker build context must be `backend` because the Dockerfile copies backend-local paths:

```bash
docker build -t opsiq-backend ./backend
docker run --rm \
  --name opsiq-backend \
  -p 8080:8080 \
  -e GEMINI_API_KEY= \
  -e CHROMA_DB_PATH=/data/chroma_db \
  -e CORS_ORIGINS=http://localhost:5173 \
  -v opsiq-chroma:/data/chroma_db \
  opsiq-backend
```

Then verify `http://127.0.0.1:8080/health`. The image excludes `.env` files, virtual environments, caches, uploaded files, logs, and local ChromaDB state.

The first retrieval or indexing request initializes ChromaDB and downloads the configured sentence-transformer and cross-encoder models. `/health` does not trigger those downloads and does not require Gemini credentials.

## Railway backend deployment

Create a Railway service from this repository and configure:

- Branch: the branch intended for deployment.
- Root Directory: `/backend`.
- Config file path: `/railway.json` (Railway config-file lookup does not follow Root Directory automatically).
- Dockerfile path: `Dockerfile`, relative to `/backend`.
- Health-check path: `/health`.
- Container port: `8080`. The Docker image listens on `0.0.0.0:8080`; Railway routes public traffic to the detected listening port.
- Persistent volume: mount a volume at `/data` and set `CHROMA_DB_PATH=/data/chroma_db`.
- `GEMINI_API_KEY`: configure as a Railway secret when synthesis is required.
- `CORS_ORIGINS`: set to the exact deployed frontend origin, without a trailing path.
- Frontend `VITE_API_URL`: set at frontend build time to the Railway backend public URL plus `/api`.

Railway deployment steps:

1. Create a service from `tauqxxr7/opsiq`.
2. Apply the root directory and config-file settings above.
3. Attach the `/data` persistent volume.
4. Add backend variables in the Railway service.
5. Deploy and wait for `/health` to pass.
6. Configure the frontend build with the resulting backend URL and add its origin to `CORS_ORIGINS`.
7. Rebuild both services after changing either origin or API URL.

No deployment URL is committed or assumed. Refer to Railway's official [Dockerfile](https://docs.railway.com/builds/dockerfiles), [monorepo](https://docs.railway.com/deployments/monorepo), and [config-as-code](https://docs.railway.com/config-as-code/reference) documentation.

## Verification

```bash
cd backend
python -m pytest -q
python -m compileall -q .
python -c "from main import app; print(app.title)"

cd ../frontend
npm ci
npm run lint
npm run build
```

## Deployment limitations

- Initial ML model downloads require outbound network access and increase first-use latency and disk consumption.
- ChromaDB requires a persistent volume; container-local data is lost on redeploy.
- The current frontend bundle should be code-split before large-scale production use.
- Local ChromaDB is suitable for the MVP and one backend replica. Multi-replica production requires coordinated or managed vector storage.
- Gemini synthesis is unavailable without `GEMINI_API_KEY`, while health checks and non-Gemini startup remain operational.

## Safety contract

OPSIQ never synthesises an answer without retrieved evidence. Empty retrieval returns “Insufficient documentation found.” Secrets remain server-side, uploads are deleted after indexing, client requests have bounded timeouts, and generated knowledge answers include source metadata.

## Built for

**ET AI Hackathon 2.0 · Phase 2 · Problem Statement #8**

Tauqeer Sameer Bharde · [github.com/tauqxxr7](https://github.com/tauqxxr7)
