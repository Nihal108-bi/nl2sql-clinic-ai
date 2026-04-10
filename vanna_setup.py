"""
vanna_setup.py  (project root)
────────────────────────────────────────────────────────────────────────────────
Alias so the assignment's required file `vanna_setup.py` exists at the project root.
The real implementation lives in app/core/vanna_setup.py.
"""

from app.core.vanna_setup import get_agent, get_memory, VANNA_AVAILABLE  # noqa: F401

__all__ = ["get_agent", "get_memory", "VANNA_AVAILABLE"]
