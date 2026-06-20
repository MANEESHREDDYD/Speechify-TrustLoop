import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent
DEMO_DATA_DIR = PROJECT_ROOT / "demo-data"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 's-trustloop.db'}")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
