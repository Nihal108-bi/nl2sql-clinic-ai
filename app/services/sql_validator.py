"""
app/services/sql_validator.py
SQL Safety Validator — runs before ANY generated SQL is executed.

Rules (from the assignment):
  1. Must be a SELECT statement.
  2. No DML / DDL: INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE.
  3. No dangerous stored-procedure keywords: EXEC, xp_, sp_, GRANT, REVOKE, SHUTDOWN.
  4. No access to SQLite system tables: sqlite_master, sqlite_sequence, etc.
"""

import re
from app.core.logger import logger

# ── Blocked keyword patterns ──────────────────────────────────────────────────
_DML_DDL = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "CREATE", "TRUNCATE", "REPLACE", "MERGE",
}
_DANGEROUS = {
    "EXEC", "EXECUTE", "XP_", "SP_",
    "GRANT", "REVOKE", "SHUTDOWN", "ATTACH", "DETACH",
}
_SYSTEM_TABLES = {
    "SQLITE_MASTER", "SQLITE_SEQUENCE", "SQLITE_STAT1",
    "SQLITE_TEMP_MASTER",
}

_ALL_BLOCKED: set[str] = _DML_DDL | _DANGEROUS | _SYSTEM_TABLES


def _normalise(sql: str) -> str:
    """Strip comments and collapse whitespace for reliable matching."""
    # Remove single-line comments
    sql = re.sub(r"--[^\n]*", " ", sql)
    # Remove block comments
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    return sql.upper()


def validate_sql(sql: str) -> tuple[bool, str]:
    """
    Validate a SQL string.

    Returns:
        (True, "")          — query is safe, proceed.
        (False, reason_str) — query is blocked, reason_str explains why.
    """
    if not sql or not sql.strip():
        return False, "Empty SQL query."

    normalised = _normalise(sql)

    # 1. Must start with SELECT (after stripping leading whitespace / CTEs)
    #    Allow WITH ... SELECT (CTE) as well.
    stripped = normalised.lstrip()
    if not (stripped.startswith("SELECT") or stripped.startswith("WITH")):
        return False, (
            "Only SELECT queries are allowed. "
            f"Your query starts with: {sql.strip().split()[0].upper()!r}"
        )

    # 2. Reject blocked keywords appearing anywhere in the query
    #    Use word-boundary matching to avoid false positives
    #    (e.g. "description" should not match "EXEC" in "DEscription").
    for keyword in _ALL_BLOCKED:
        # Use word boundary for normal words; prefix match for xp_ / sp_
        if keyword.endswith("_"):
            pattern = rf"\b{re.escape(keyword)}"
        else:
            pattern = rf"\b{re.escape(keyword)}\b"
        if re.search(pattern, normalised):
            logger.warning(f"SQL validation blocked keyword '{keyword}' in query: {sql[:80]}")
            return False, f"Unsafe keyword detected: '{keyword}'. Query rejected."

    logger.debug(f"SQL validation passed: {sql[:80]}")
    return True, ""
