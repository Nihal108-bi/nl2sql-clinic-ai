"""
app/main.py
────────────────────────────────────────────────────────────────────────────────
FastAPI Application Entry Point

Features:
  ✅ Custom Swagger UI (branded, dark theme, custom logo)
  ✅ ReDoc documentation
  ✅ Per-IP rate limiting via slowapi
  ✅ CORS enabled
  ✅ Request/response logging middleware
  ✅ Startup / shutdown lifecycle hooks
  ✅ /health and /chat routes
"""

import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.api.routes import router
from app.core.config import settings
from app.core.logger import logger
import os

# ── Rate Limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

# ── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="🏥 NL2SQL Clinic Intelligence API",
    description="""
## Natural Language to SQL — Clinic Management System

Ask questions in **plain English** and get instant answers from the clinic database.

### Features
- 🤖 **AI-Powered** — Google Gemini 2.5 Flash (Vanna 2.0 Agent)
- 🔒 **SQL Validation** — Only safe SELECT queries are executed
- 📊 **Auto Charts** — Plotly visualisations generated automatically
- 🧠 **Memory** — Learns from past correct queries
- ⚡ **Caching** — Repeated questions are served instantly
- 🚦 **Rate Limiting** — 10 requests/minute per IP

### Quick Start
```bash
POST /chat
{ "question": "How many patients do we have?" }
```

### LLM Provider
Using: **Google Gemini 2.5 Flash** via AI Studio (free tier)
    """,
    version="1.0.0",
    contact={
        "name": "AI/ML Intern Assignment",
        "email": "intern@clinic.local",
    },
    license_info={
        "name": "MIT",
    },
    # Disable default docs so we can serve custom ones
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
)

# ── Attach limiter ────────────────────────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request Logging Middleware ────────────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = round((time.perf_counter() - start) * 1000, 1)
    logger.info(
        f"{request.method} {request.url.path} "
        f"-> {response.status_code} [{elapsed}ms]"
    )
    return response

# ── Lifecycle ─────────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    os.makedirs("logs", exist_ok=True)
    logger.info("=" * 60)
    logger.info("  NL2SQL Clinic API starting up…")
    logger.info(f"  LLM Provider : {settings.LLM_PROVIDER}")
    logger.info(f"  Database     : {settings.DB_PATH}")
    logger.info(f"  Cache TTL    : {settings.CACHE_TTL_SECONDS}s")
    logger.info(f"  Rate Limit   : {settings.RATE_LIMIT}")
    logger.info("=" * 60)

    # Pre-warm Vanna agent
    try:
        from app.core.vanna_setup import get_agent
        get_agent()
    except Exception as e:
        logger.warning(f"Agent pre-warm skipped: {e}")


@app.on_event("shutdown")
async def shutdown():
    logger.info("NL2SQL Clinic API shutting down.")


# ── Custom Swagger UI (branded) ───────────────────────────────────────────────
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return HTMLResponse(content=f"""
<!DOCTYPE html>
<html>
<head>
  <title>🏥 NL2SQL Clinic API — Docs</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" type="text/css"
        href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" >
  <style>
    /* ── Custom Branding ── */
    body {{ background: #0f172a; margin: 0; }}

    .swagger-ui .topbar {{
      background: linear-gradient(135deg, #1e3a5f 0%, #0f766e 100%);
      padding: 12px 24px;
      display: flex; align-items: center; gap: 16px;
    }}
    .swagger-ui .topbar .topbar-wrapper {{
      display: flex; align-items: center; gap: 12px; flex: 1;
    }}
    .swagger-ui .topbar .topbar-wrapper::before {{
      content: "🏥 NL2SQL Clinic Intelligence API";
      font-size: 1.2rem; font-weight: 700; color: #fff;
      font-family: 'Segoe UI', sans-serif; white-space: nowrap;
    }}
    .swagger-ui .topbar img {{ display: none; }}
    .swagger-ui .topbar a {{ display: none; }}

    /* ── Background ── */
    .swagger-ui {{ background: #0f172a; color: #e2e8f0; }}
    .swagger-ui .wrapper {{ background: #0f172a; }}
    .swagger-ui .info {{ background: #1e293b; border-radius: 12px;
                         padding: 24px; margin: 20px 0; }}
    .swagger-ui .info .title {{ color: #38bdf8; }}
    .swagger-ui .info p, .swagger-ui .info li {{ color: #94a3b8; }}

    /* ── Operation blocks ── */
    .swagger-ui .opblock.opblock-post .opblock-summary {{
      background: rgba(16,185,129,0.1);
      border-color: #10b981;
    }}
    .swagger-ui .opblock.opblock-get .opblock-summary {{
      background: rgba(59,130,246,0.1);
      border-color: #3b82f6;
    }}
    .swagger-ui .opblock-summary-method {{
      border-radius: 6px; font-weight: 700;
    }}
    .swagger-ui .opblock-body {{ background: #1e293b; }}

    /* ── Badges ── */
    .swagger-ui .model-box {{ background: #1e293b; border-radius: 8px; }}
    .swagger-ui input[type=text], .swagger-ui textarea {{
      background: #0f172a; color: #e2e8f0;
      border: 1px solid #334155; border-radius: 6px;
    }}
    .swagger-ui .btn.execute {{
      background: #10b981; color: white;
      border-radius: 6px; font-weight: 600;
    }}
    .swagger-ui .btn.execute:hover {{ background: #059669; }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: #0f172a; }}
    ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 3px; }}
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"> </script>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"> </script>
  <script>
    window.onload = function() {{
      const ui = SwaggerUIBundle({{
        url: "/openapi.json",
        dom_id: '#swagger-ui',
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        layout: "StandaloneLayout",
        deepLinking: true,
        displayRequestDuration: true,
        defaultModelsExpandDepth: 2,
        defaultModelExpandDepth: 2,
        tryItOutEnabled: true,
        filter: true,
        syntaxHighlight: {{ theme: "agate" }},
      }})
      window.ui = ui
    }}
  </script>
</body>
</html>
""")


# ── Custom ReDoc ──────────────────────────────────────────────────────────────
@app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
  <title>NL2SQL Clinic API — ReDoc</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700"
        rel="stylesheet">
  <style> body { margin: 0; padding: 0; } </style>
</head>
<body>
  <redoc spec-url='/openapi.json'
         theme='{
           "colors": {
             "primary": { "main": "#0f766e" },
             "success": { "main": "#10b981" }
           },
           "typography": { "fontSize": "15px", "fontFamily": "Roboto, sans-serif" },
           "sidebar": { "backgroundColor": "#0f172a", "textColor": "#e2e8f0" }
         }'></redoc>
  <script src="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js"></script>
</body>
</html>
""")


# ── Include Routes ────────────────────────────────────────────────────────────
app.include_router(router)


# ── Root redirect ─────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse({
        "message": "🏥 NL2SQL Clinic Intelligence API",
        "docs":    "/docs",
        "redoc":   "/redoc",
        "health":  "/health",
        "chat":    "POST /chat",
    })
