import nest_asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.config import settings
from src.api.routes import router as api_router

# Allows synchronous agent functions to invoke async MCP helpers inside FastAPI
nest_asyncio.apply()


def create_application() -> FastAPI:
    """Application factory for TripMate AI FastAPI service."""
    app = FastAPI(
        title="TripMate AI",
        description=(
            "LangGraph Multi-Agent Travel Planner with Supervisor, Guardrails, "
            "Human-in-the-Loop, and FastAPI Frontend"
        ),
        version="2.0.0",
    )

    # Explicit static asset handlers
    @app.get("/static/style.css", tags=["Static"])
    async def get_style():
        css_path = settings.STATIC_DIR / "style.css"
        return Response(content=css_path.read_text(encoding="utf-8"), media_type="text/css")

    @app.get("/static/script.js", tags=["Static"])
    async def get_script():
        js_path = settings.STATIC_DIR / "script.js"
        return Response(content=js_path.read_text(encoding="utf-8"), media_type="application/javascript")

    templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

    # Mount API router
    app.include_router(api_router)

    # Frontend routes
    @app.get("/", response_class=HTMLResponse, tags=["Frontend"])
    async def home(request: Request):
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={},
        )

    @app.get("/health", tags=["Diagnostics"])
    async def root_health_check():
        return {
            "status": "ok",
            "message": "TripMate AI API is running",
            "features": [
                "supervisor_agent",
                "input_guardrail",
                "human_in_the_loop",
            ],
        }

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return JSONResponse(content={})

    return app


app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
