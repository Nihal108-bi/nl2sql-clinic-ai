"""
app/core/vanna_setup.py  (also importable as vanna_setup.py from project root)
────────────────────────────────────────────────────────────────────────────────
Vanna 2.0 Agent Initialisation

Supports four LLM backends — set LLM_PROVIDER in .env:
  • gemini  (default) — Google Gemini 2.5 Flash via AI Studio
  • groq             — Groq / Llama-3.3-70b
  • openai           — OpenAI / GPT-4.1 mini
  • ollama           — local Ollama instance

Architecture:
  GeminiLlmService / OpenAILlmService
    └─ Agent
         ├─ RunSqlTool          → executes validated SELECT queries
         ├─ VisualizeDataTool   → Plotly chart generation (built-in)
         ├─ SaveQuestionToolArgsTool   ┐
         ├─ SearchSavedCorrectToolUsesTool ┤ memory tools
         └─ SaveTextMemoryTool          ┘
"""

from app.core.config import settings
from app.core.logger import logger

# ── Vanna 2.0 imports ─────────────────────────────────────────────────────────
try:
    from vanna import Agent
    from vanna.core.registry import ToolRegistry
    from vanna.core.user import UserResolver, User, RequestContext
    from vanna.tools import RunSqlTool, VisualizeDataTool
    from vanna.tools.agent_memory import (
        SaveQuestionToolArgsTool,
        SearchSavedCorrectToolUsesTool,
        SaveTextMemoryTool,
    )
    from vanna.integrations.sqlite import SqliteRunner
    from vanna.integrations.local.agent_memory import DemoAgentMemory
    VANNA_AVAILABLE = True
    logger.info("Vanna 2.0 imported successfully.")
except ImportError as e:
    VANNA_AVAILABLE = False
    logger.warning(f"Vanna 2.0 not available ({e}). Falling back to direct SQLite mode.")


# ── LLM Service ───────────────────────────────────────────────────────────────
def _build_llm(provider: str | None = None):
    provider = (provider or settings.LLM_PROVIDER).lower()

    if provider == "gemini":
        from vanna.integrations.google import GeminiLlmService
        logger.info(f"LLM: Google Gemini ({settings.GEMINI_MODEL})")
        return GeminiLlmService(
            model=settings.GEMINI_MODEL,
            api_key=settings.GOOGLE_API_KEY,
        )

    elif provider == "groq":
        from vanna.integrations.openai import OpenAILlmService
        logger.info(f"LLM: Groq / {settings.GROQ_MODEL}")
        return OpenAILlmService(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )

    elif provider == "openai":
        from vanna.integrations.openai import OpenAILlmService
        logger.info(f"LLM: OpenAI / {settings.OPENAI_MODEL}")
        return OpenAILlmService(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )

    elif provider == "ollama":
        from vanna.integrations.openai import OpenAILlmService
        logger.info(f"LLM: Ollama / {settings.OLLAMA_MODEL}")
        return OpenAILlmService(
            model=settings.OLLAMA_MODEL,
            api_key="ollama",           # Ollama doesn't need a real key
            base_url=settings.OLLAMA_BASE_URL,
        )

    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider!r}")


# ── User Resolver ─────────────────────────────────────────────────────────────
class SimpleUserResolver(UserResolver):
    """
    Resolves every incoming request to a single 'default_user'.
    In production you would map JWT claims → User here.
    """
    async def resolve_user(self, request_context: RequestContext) -> User:
        return User(
            id="default_user",
            email="user@clinic.local",
            group_memberships=["user", "admin"],
        )


# ── Build Agent ───────────────────────────────────────────────────────────────
_agents: dict[str, Agent] = {}
_memories: dict[str, DemoAgentMemory] = {}

def get_agent(provider: str | None = None):
    provider = (provider or settings.LLM_PROVIDER).lower()
    if provider in _agents:
        return _agents[provider]

    if not VANNA_AVAILABLE:
        logger.warning("Returning None agent — Vanna not installed.")
        return None

    llm            = _build_llm(provider)
    db_tool        = RunSqlTool(sql_runner=SqliteRunner(database_path=settings.DB_PATH))
    memory         = DemoAgentMemory(max_items=2000)
    user_resolver  = SimpleUserResolver()

    tools = ToolRegistry()
    tools.register_local_tool(db_tool,                          access_groups=["admin", "user"])
    tools.register_local_tool(VisualizeDataTool(),              access_groups=["admin", "user"])
    tools.register_local_tool(SaveQuestionToolArgsTool(),       access_groups=["admin"])
    tools.register_local_tool(SearchSavedCorrectToolUsesTool(), access_groups=["admin", "user"])
    tools.register_local_tool(SaveTextMemoryTool(),             access_groups=["admin", "user"])

    agent = Agent(
        llm_service=llm,
        tool_registry=tools,
        user_resolver=user_resolver,
        agent_memory=memory,
    )
    _agents[provider] = agent
    _memories[provider] = memory
    logger.info(f"Vanna 2.0 Agent initialised for provider={provider}.")
    return agent


def get_memory(provider: str | None = None):
    """Return the DemoAgentMemory instance (initialise agent first if needed)."""
    provider = (provider or settings.LLM_PROVIDER).lower()
    if provider not in _memories:
        get_agent(provider)
    return _memories.get(provider)
