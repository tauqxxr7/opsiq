# Deploying OPSIQ

## Backend — Railway

1. Go to railway.app and create a New Project
2. Select Deploy from GitHub repo → tauqxxr7/opsiq
3. Set Root Directory to: backend
4. Add environment variables:
   - GEMINI_API_KEY = your_key_here
   - CHROMA_DB_PATH = /data/chroma_db
   - CORS_ORIGINS = https://your-vercel-url.vercel.app
5. Add a volume mount at /data
6. Deploy. Health check: /health

## Frontend — Vercel

1. Go to vercel.com → New Project
2. Import tauqxxr7/opsiq from GitHub
3. Set Root Directory to: frontend
4. Add environment variable:
   - VITE_API_URL = https://your-railway-url.railway.app/api
5. Deploy.

## Local Development

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp ../.env.example .env
# Add GEMINI_API_KEY to .env
uvicorn main:app --reload --port 8000

# New terminal
cd frontend
npm install
npm run dev
# Open http://localhost:5173
```
