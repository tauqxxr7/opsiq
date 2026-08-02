# Deploying OPSIQ

## Backend — Railway

1. Create a Railway project from `tauqxxr7/opsiq`.
2. Set the service root directory to `backend`.
3. Mount a persistent volume at `/data`.
4. Configure:
   - `GEMINI_API_KEY` — optional synthesis key
   - `CHROMA_DB_PATH=/data/chroma_db`
   - `OPSIQ_DB_PATH=/data/opsiq.db`
   - `CORS_ORIGINS=https://your-vercel-url.vercel.app`
   - `OPSIQ_AUTH_REQUIRED=true`
   - `OPSIQ_JWT_SECRET` — a random secret of at least 32 characters
   - `OPSIQ_ADMIN_USERNAME` — bootstrap administrator username
   - `OPSIQ_ADMIN_PASSWORD` — unique bootstrap password of at least 12 characters
   - `OPSIQ_ADMIN_DISPLAY_NAME` — administrator display name
5. Deploy and use `/health` as the health check.

The bootstrap administrator is created only if the configured username does not exist. Remove the bootstrap password from the Railway environment after the first successful initialization. SQLite is suitable for the single-instance demonstration; PostgreSQL and refresh-token revocation are required before multi-instance enterprise use.

## Frontend — Vercel

1. Import `tauqxxr7/opsiq` into Vercel.
2. Set the root directory to `frontend`.
3. Configure:
   - `VITE_API_URL=https://your-railway-url.railway.app/api`
   - `VITE_AUTH_REQUIRED=true`
4. Deploy. The checked-in rewrites support direct access to application and login routes.

## Local development

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item ../.env.example .env
uvicorn main:app --reload --host 127.0.0.1 --port 8000

# New terminal
cd frontend
npm ci
npm run dev -- --host 127.0.0.1
```

Authentication defaults to disabled for backward-compatible local demonstration. To test it locally, enable both `OPSIQ_AUTH_REQUIRED=true` and `VITE_AUTH_REQUIRED=true`, provide the JWT secret and bootstrap administrator variables, then restart both services.
