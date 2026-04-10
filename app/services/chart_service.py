"""
app/services/chart_service.py
Automatic Plotly chart generation from query results.

Heuristics:
  • 1 numeric column  → bar chart (categories on x-axis)
  • 2 numeric columns → scatter / line
  • date column + numeric → line chart (time series)
  • Otherwise         → table (no chart)
"""

import json
import re
from typing import Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from app.core.logger import logger


def _is_date_col(col: str) -> bool:
    keywords = ("date", "month", "year", "week", "day", "time", "period")
    return any(k in col.lower() for k in keywords)


def _is_numeric_col(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)


def generate_chart(
    columns: list[str],
    rows: list[list],
    question: str = "",
) -> tuple[Optional[dict], str]:
    """
    Build a Plotly figure dict from query result columns + rows.

    Returns:
        (chart_json_dict, chart_type_str)   — on success
        (None, "none")                       — when no chart makes sense
    """
    if not rows or not columns:
        return None, "none"

    try:
        df = pd.DataFrame(rows, columns=columns)

        numeric_cols = [c for c in df.columns if _is_numeric_col(df[c])]
        date_cols    = [c for c in df.columns if _is_date_col(c)]
        text_cols    = [c for c in df.columns if c not in numeric_cols]

        if not numeric_cols:
            return None, "none"

        fig = None
        chart_type = "bar"

        # ── Time series ───────────────────────────────────────────────────
        if date_cols and numeric_cols:
            x_col = date_cols[0]
            y_col = numeric_cols[0]
            # Sort by date for a clean line
            try:
                df[x_col] = pd.to_datetime(df[x_col])
                df = df.sort_values(x_col)
            except Exception:
                pass
            fig = px.line(
                df, x=x_col, y=y_col,
                title=question or "Trend over time",
                markers=True,
            )
            chart_type = "line"

        # ── Single categorical + numeric (bar) ────────────────────────────
        elif len(numeric_cols) == 1 and text_cols:
            x_col = text_cols[0]
            y_col = numeric_cols[0]
            df = df.sort_values(y_col, ascending=False).head(20)
            fig = px.bar(
                df, x=x_col, y=y_col,
                title=question or "Distribution",
                color=y_col,
                color_continuous_scale="Blues",
            )
            chart_type = "bar"

        # ── Two numeric columns → scatter ─────────────────────────────────
        elif len(numeric_cols) >= 2:
            fig = px.scatter(
                df, x=numeric_cols[0], y=numeric_cols[1],
                title=question or "Relationship",
            )
            chart_type = "scatter"

        # ── Pure numeric (single) + no categories → bar of index ─────────
        elif len(numeric_cols) == 1:
            y_col = numeric_cols[0]
            fig = px.bar(df, y=y_col, title=question or "Values")
            chart_type = "bar"

        if fig is None:
            return None, "none"

        # Clean up layout
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=40, r=40, t=60, b=40),
        )

        chart_dict = json.loads(fig.to_json())
        logger.debug(f"Chart generated: type={chart_type}")
        return chart_dict, chart_type

    except Exception as e:
        logger.warning(f"Chart generation failed: {e}")
        return None, "none"
