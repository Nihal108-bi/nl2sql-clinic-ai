"""
main.py  (project root)
────────────────────────────────────────────────────────────────────────────────
Root entry point so the assignment's required command works:

    uvicorn main:app --port 8000

Simply re-exports the FastAPI `app` from app/main.py.
"""

from app.main import app  # noqa: F401 — re-export

__all__ = ["app"]
