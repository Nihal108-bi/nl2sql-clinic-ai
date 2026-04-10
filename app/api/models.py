"""
app/api/models.py
Pydantic models for API request and response validation.
"""

from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


# ── Request ───────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural-language question about the clinic database.",
        examples=["How many patients do we have?"],
    )

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Question cannot be blank.")
        return stripped


# ── Response ──────────────────────────────────────────────────────────────────

class ChatResponse(BaseModel):
    message: str = Field(description="Human-readable answer / summary.")
    sql_query: Optional[str] = Field(default=None, description="Generated SQL.")
    columns: Optional[list[str]] = Field(default=None, description="Column names.")
    rows: Optional[list[list[Any]]] = Field(default=None, description="Result rows.")
    row_count: Optional[int] = Field(default=None, description="Number of rows returned.")
    chart: Optional[dict] = Field(default=None, description="Plotly JSON chart.")
    chart_type: Optional[str] = Field(default="none", description="Chart type used.")
    cached: bool = Field(default=False, description="True if result was served from cache.")
    error: Optional[str] = Field(default=None, description="Error message if something went wrong.")


class HealthResponse(BaseModel):
    status: str
    database: str
    agent_memory_items: int
    llm_provider: str
