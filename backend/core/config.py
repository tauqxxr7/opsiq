import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]


def _csv_env(name: str, default: str) -> list[str]:
    return [value.strip() for value in os.getenv(name, default).split(",") if value.strip()]


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
CHROMA_DB_PATH = os.getenv(
    "CHROMA_DB_PATH", str(BASE_DIR / "data" / "chroma_db")
)
CORS_ORIGINS = _csv_env(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
)
