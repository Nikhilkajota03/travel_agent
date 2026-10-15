# TripMate AI: Multi-Agent System using LangGraph, MCP, Supervisor, Guardrails & HITL

A production-grade multi-agent travel-planning platform powered by **LangGraph**, **Model Context Protocol (MCP)**, **Groq LLaMA 3.3**, and **FastAPI**. It features an intelligent **Supervisor Agent**, input **Guardrails**, specialist domain agents, PostgreSQL-backed checkpointing, and **Human-in-the-Loop (HITL)** approval flows.

---

## Architecture Overview

```
User Input ──▶ Input Guardrail ──┬─[Blocked]─▶ Guardrail Blocked Agent ──▶ END
                                 │
                                 └─[Passed]──▶ Supervisor Agent
                                                    │ (Dynamic Agent Selection)
                                                    ▼
                       ┌─────────────────────────────────────────────────────────┐
                       │                   Specialist Agents                     │
                       │  - Flight Agent (AviationStack MCP via uvx)             │
                       │  - Hotel Agent (Tavily MCP via streamable HTTP)         │
                       │  - Weather Agent (Custom OpenWeather FastMCP)           │
                       │  - Budget Agent (LLaMA 3.3)                             │
                       │  - Itinerary Agent (LLaMA 3.3)                          │
                       └─────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
                                    Human-in-the-Loop (interrupt)
                                           /                 \
                               [ Approved ]                   [ Revision Requested ]
                                         \                   /
                                          ▼                 ▼
                                    Final Response Synthesis Agent
                                                    │
                                                    ▼
                                                  END
```

---

## Production Directory Structure

```
├── src/                               # Core Application Source Package
│   ├── config.py                      # Centralized configuration & environment validation
│   ├── state.py                       # TravelState TypedDict & constraint definitions
│   │
│   ├── core/                          # Fundamental Infrastructure
│   │   ├── llm.py                     # Groq LLM client & structured JSON parsing
│   │   └── database.py                # PostgreSQL connection & PostgresSaver checkpointer
│   │
│   ├── mcp/                           # Model Context Protocol Subsystem
│   │   ├── client.py                  # MultiServerMCPClient management (Tavily, AviationStack, Weather)
│   │   ├── tools.py                   # Specialized MCP tool invocations
│   │   └── servers/
│   │       └── weather_server.py      # Custom FastMCP server for OpenWeather
│   │
│   ├── agents/                        # AI Specialist Agents
│   │   ├── prompts.py                 # Centralized prompt templates
│   │   ├── guardrail.py               # Input safety & relevance validation agent
│   │   ├── supervisor.py              # Supervisor agent for dynamic routing & decomposition
│   │   ├── flight.py                  # Flight recommendations specialist
│   │   ├── hotel.py                   # Hotel & accommodation specialist
│   │   ├── weather.py                 # Climate & weather forecast specialist
│   │   ├── budget.py                  # Budget & cost analysis specialist
│   │   ├── itinerary.py               # Day-by-day itinerary planner
│   │   ├── hitl.py                    # Human-in-the-loop review & pause node
│   │   └── final.py                   # Final plan synthesis agent
│   │
│   ├── graph/                         # LangGraph Orchestration Engine
│   │   ├── routing.py                 # Dynamic conditional edges & transition maps
│   │   ├── builder.py                 # Graph construction & checkpointer compilation
│   │   └── service.py                 # Workflow execution & thread resumption services
│   │
│   └── api/                           # HTTP & API Layer
│       ├── schemas.py                 # Pydantic request/response models
│       └── routes.py                  # FastAPI APIRouter endpoints
│
├── app.py                             # FastAPI server entrypoint & static assets mounter
├── backend.py                         # Backward-compatible facade module
├── mcp_client.py                      # Backward-compatible MCP facade module
├── custom_weather_mcp_server.py       # Weather MCP server launcher
├── static/                            # Frontend assets (CSS, JS)
├── templates/                         # Jinja2 HTML templates
├── requirements.txt                   # Project dependencies
└── Dockerfile                         # Production container image
```

---

## Prerequisites

- **Python 3.10+**
- **PostgreSQL Database** (Render Postgres, Supabase, Neon, or local)
- **uv / uvx** (for AviationStack MCP execution: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- API keys:
  - `GROQ_API_KEY`: Groq API key (for LLaMA 3.3 70B)
  - `DATABASE_URL`: PostgreSQL connection string with SSL
  - `TAVILY_API_KEY`: For hotel searches
  - `AVIATION_STACK_API_KEY`: For flight data
  - `OPENWEATHER_API_KEY`: For weather forecasting

---

## Environment Configuration

Create a `.env` file in the root folder:

```env
GROQ_API_KEY=gsk_...
DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
TAVILY_API_KEY=tvly-...
AVIATION_STACK_API_KEY=...
OPENWEATHER_API_KEY=...
```

---

## Quick Start

### 1. Set Up Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
# Or with uvicorn directly:
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## API Endpoints

- `POST /api/travel`: Create or continue a travel planning workflow.
  ```json
  { "message": "Plan a 4-day trip to Dubai for next month", "thread_id": "optional-id" }
  ```
- `POST /api/travel/approve`: Submit human review decision.
  ```json
  { "thread_id": "user_...", "approved": true, "feedback": "optional feedback" }
  ```
- `GET /api/health` and `GET /health`: Health and capability diagnostics.
