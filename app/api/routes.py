"""
app/api/routes.py
FastAPI route handlers for /chat and /health.

Features implemented:
  ✅ POST /chat  — NL → SQL → Execute → Chart
  ✅ GET /health — database + agent status
  ✅ SQL validation before execution
  ✅ Query result caching (TTL-based)
  ✅ Per-IP rate limiting (via slowapi)
  ✅ Structured logging for every step
  ✅ Graceful error handling
"""

import hashlib
import re
import time
import uuid
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from cachetools import TTLCache

from app.api.models import ChatRequest, ChatResponse, HealthResponse
from app.core.config import settings
from app.core.database import check_connection, execute_query
from app.core.logger import logger
from app.services.sql_validator import validate_sql
from app.services.chart_service import generate_chart
from vanna.core.user import RequestContext

router = APIRouter()

# ── Query Result Cache ────────────────────────────────────────────────────────
_cache: TTLCache = TTLCache(maxsize=256, ttl=settings.CACHE_TTL_SECONDS)
_provider_cooldowns: dict[str, float] = {}


def _cache_key(question: str) -> str:
    return hashlib.md5(question.lower().strip().encode()).hexdigest()


def _provider_in_cooldown(provider: str) -> bool:
    return _provider_cooldowns.get(provider, 0) > time.time()


def _set_provider_cooldown(provider: str, error_message: str) -> None:
    retry_after = 60

    retry_match = re.search(r"retry in ([0-9]+(?:\.[0-9]+)?)s", error_message, flags=re.IGNORECASE)
    if retry_match:
        retry_after = max(retry_after, int(float(retry_match.group(1))))

    seconds_match = re.search(r"retryDelay['\"]?\s*:\s*'([0-9]+)s'", error_message, flags=re.IGNORECASE)
    if seconds_match:
        retry_after = max(retry_after, int(seconds_match.group(1)))

    _provider_cooldowns[provider] = time.time() + retry_after
    logger.warning(f"[CHAT] {provider} temporarily disabled for {retry_after}s after upstream quota/rate-limit error.")


def _provider_candidates() -> list[str]:
    primary = settings.LLM_PROVIDER.lower()
    ordered = [primary]
    for candidate in ("gemini", "openai", "groq"):
        if candidate != primary:
            ordered.append(candidate)
    return ordered


def _extract_rows_from_component(component: Any) -> tuple[list[str], list[list[Any]]]:
    """Convert a Vanna DataFrame-like rich component into API response rows."""
    rich = getattr(component, "rich_component", None)
    if rich is None:
        return [], []

    component_type = getattr(rich, "type", None)
    if str(component_type).lower() != "componenttype.dataframe":
        return [], []

    records = getattr(rich, "rows", None) or []
    columns = getattr(rich, "columns", None) or []
    if not records:
        return list(columns), []

    if not columns and isinstance(records[0], dict):
        columns = list(records[0].keys())

    row_values = []
    for record in records:
        if isinstance(record, dict):
            row_values.append([record.get(col) for col in columns])

    return list(columns), row_values


async def _extract_sql_from_conversation(agent: Any, ctx: RequestContext, conversation_id: str) -> str | None:
    """Read the latest run_sql tool call from the stored Vanna conversation."""
    try:
        user = await agent.user_resolver.resolve_user(ctx)
        conversation = await agent.conversation_store.get_conversation(conversation_id, user)
        if not conversation:
            return None

        for message in reversed(conversation.messages):
            for tool_call in reversed(message.tool_calls or []):
                if tool_call.name == "run_sql":
                    sql = tool_call.arguments.get("sql")
                    if isinstance(sql, str) and sql.strip():
                        return sql.strip()
    except Exception as exc:
        logger.warning(f"[CHAT] Could not extract SQL from conversation: {exc}")

    return None


async def _run_agent_query(request: Request, question: str, provider_name: str) -> tuple[str | None, list, list, str, str | None]:
    from app.core.vanna_setup import get_agent

    agent = get_agent(provider_name)
    conversation_id = str(uuid.uuid4())
    ctx = RequestContext(
        remote_addr=request.client.host if request.client else None,
        headers={k: v for k, v in request.headers.items()},
        metadata={"path": str(request.url.path), "provider": provider_name},
    )

    columns: list = []
    rows: list = []
    text_parts: list[str] = []

    async for chunk in agent.send_message(ctx, question, conversation_id=conversation_id):
        simple = getattr(chunk, "simple_component", None)
        if simple is not None:
            text_piece = getattr(simple, "text", None)
            if text_piece and isinstance(text_piece, str):
                text_parts.append(text_piece.strip())

        if not rows:
            extracted_columns, extracted_rows = _extract_rows_from_component(chunk)
            if extracted_columns or extracted_rows:
                columns = extracted_columns
                rows = extracted_rows

    sql_query = await _extract_sql_from_conversation(agent, ctx, conversation_id)
    if text_parts:
        message = text_parts[-1]
    elif rows:
        message = f"Found {len(rows)} result(s)."
    else:
        message = "Query completed."

    error = None
    if message.startswith("Error:"):
        error = message.removeprefix("Error:").strip()

    return sql_query, columns, rows, message, error


# ── /health ───────────────────────────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns the status of the API, database connection, and agent memory.",
    tags=["System"],
)
def health_check():
    from app.core.vanna_setup import get_memory
    db_ok  = check_connection()
    memory = get_memory()
    mem_count = len(memory.items) if memory and hasattr(memory, 'items') else 0

    return HealthResponse(
        status="ok",
        database="connected" if db_ok else "disconnected",
        agent_memory_items=mem_count,
        llm_provider=settings.LLM_PROVIDER,
    )


# ── /chat ─────────────────────────────────────────────────────────────────────

@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Ask a Question",
    description=(
        "Send a natural-language question about the clinic database. "
        "The system generates SQL, validates it, executes it, and returns "
        "results with an optional Plotly chart."
    ),
    tags=["NL2SQL"],
)
async def chat(request: Request, body: ChatRequest):
    question = body.question
    start    = time.perf_counter()
    logger.info(f"[CHAT] Question: {question!r}")

    # ── 1. Cache check ────────────────────────────────────────────────────
    key = _cache_key(question)
    if key in _cache:
        logger.info("[CHAT] Cache HIT")
        cached_response = _cache[key]
        cached_response["cached"] = True
        return ChatResponse(**cached_response)

    # ── 2. Try Vanna agent ────────────────────────────────────────────────
    sql_query: str | None  = None
    columns:   list        = []
    rows:      list        = []
    message:   str         = ""
    error:     str | None  = None

    try:
        from app.core.vanna_setup import VANNA_AVAILABLE

        if VANNA_AVAILABLE:
            for provider_name in _provider_candidates():
                if _provider_in_cooldown(provider_name):
                    logger.warning(f"{provider_name} is in cooldown — skipping to next provider.")
                    continue

                logger.info(f"[CHAT] Trying provider={provider_name}")
                sql_query, columns, rows, message, error = await _run_agent_query(
                    request, question, provider_name
                )

                if rows or sql_query:
                    if provider_name != settings.LLM_PROVIDER.lower():
                        message = f"Answered using backup provider: {provider_name}."
                    break

                if error:
                    _set_provider_cooldown(provider_name, error)
                    logger.warning(f"[CHAT] Provider {provider_name} failed, trying next provider.")

            if not sql_query and not rows:
                error = error or "All configured AI providers are temporarily unavailable."

        else:
            # ── Fallback: bare SQL execution (no LLM) ────────────────────
            logger.warning("Vanna unavailable — using fallback SQL execution mode.")
            sql_query = _fallback_sql_for_question(question)
            if sql_query:
                result_dicts = execute_query(sql_query)
                if result_dicts:
                    columns = list(result_dicts[0].keys())
                    rows    = [list(r.values()) for r in result_dicts]
                message = f"Executed fallback query. {len(rows)} row(s) returned."
            else:
                message = "Could not generate SQL for this question in fallback mode."

    except Exception as e:
        logger.error(f"[CHAT] Agent error: {e}")
        return ChatResponse(
            message="Sorry, the AI agent encountered an error.",
            error=str(e),
        )

    # ── 3. SQL Validation ─────────────────────────────────────────────────
    if (error or not sql_query) and not rows:
        fallback_sql = _fallback_sql_for_question(question)
        if fallback_sql:
            logger.warning("[CHAT] Using fallback SQL because the AI provider did not return an executable query.")
            sql_query = fallback_sql
            error = None
            if not message or message.startswith("Error:"):
                message = "Using fallback query because the AI provider is temporarily unavailable."

    if sql_query:
        valid, reason = validate_sql(sql_query)
        if not valid:
            logger.warning(f"[CHAT] SQL validation failed: {reason}")
            return ChatResponse(
                message=f"Query blocked by safety validator: {reason}",
                sql_query=sql_query,
                error=reason,
            )

    # ── 4. Execute directly if Vanna didn't return data ───────────────────
    if sql_query and not rows:
        try:
            result_dicts = execute_query(sql_query)
            if result_dicts:
                columns = list(result_dicts[0].keys())
                rows    = [list(r.values()) for r in result_dicts]
                if not message:
                    message = f"Found {len(rows)} result(s)."
        except Exception as e:
            logger.error(f"[CHAT] DB execution error: {e}")
            return ChatResponse(
                message="Database query failed.",
                sql_query=sql_query,
                error=str(e),
            )

    if not rows and sql_query:
        message = message or "No data found for your query."

    # ── 5. Chart generation ───────────────────────────────────────────────
    chart, chart_type = generate_chart(columns, rows, question)

    # ── 6. Build response ─────────────────────────────────────────────────
    elapsed = round((time.perf_counter() - start) * 1000, 1)
    logger.info(f"[CHAT] Done in {elapsed}ms | rows={len(rows)} | chart={chart_type}")

    response_data: dict[str, Any] = {
        "message":    message or f"Returned {len(rows)} row(s).",
        "sql_query":  sql_query,
        "columns":    columns or None,
        "rows":       rows    or None,
        "row_count":  len(rows),
        "chart":      chart,
        "chart_type": chart_type,
        "cached":     False,
        "error":      error,
    }

    # Store in cache
    _cache[key] = response_data.copy()

    return ChatResponse(**response_data)


# ── Fallback SQL map (used when Vanna is not installed) ───────────────────────

def _fallback_sql_for_question(question: str) -> str | None:
    """Very simple keyword → SQL mapping for demo purposes."""
    q = question.lower()
    if "how many patients" in q:
        return "SELECT COUNT(*) as total_patients FROM patients"
    if "all doctors" in q or "list doctors" in q:
        return "SELECT name, specialization, department FROM doctors ORDER BY name"
    if "total revenue" in q:
        return "SELECT SUM(total_amount) as total_revenue FROM invoices"
    if "unpaid" in q or "pending" in q:
        return "SELECT * FROM invoices WHERE status IN ('Pending', 'Overdue')"
    if "top 5 patients" in q:
        return """
            SELECT p.first_name, p.last_name, SUM(i.total_amount) as total_spending
            FROM patients p JOIN invoices i ON p.id = i.patient_id
            GROUP BY p.id ORDER BY total_spending DESC LIMIT 5
        """
    return None
