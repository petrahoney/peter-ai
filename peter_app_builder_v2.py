"""
peter_app_builder_v2.py
PETER App Builder ULTIMATE
Full-Stack: FastAPI + React/HTML + MongoDB + Docker + VPS Deploy
Support: Web App, Mobile API, Bot (Telegram/Discord/WhatsApp)
"""

import os
import sys
import json
import subprocess
import shutil
import time
sys.path.append("C:\\peter-ai")

from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
USER_NAME     = os.getenv("USER_NAME", "Sir")
APPS_DIR      = "C:\\peter-ai\\apps"
os.makedirs(APPS_DIR, exist_ok=True)

# VPS Config dari .env
VPS_HOST = os.getenv("VPS_HOST", "")
VPS_USER = os.getenv("VPS_USER", "root")
VPS_KEY  = os.getenv("VPS_KEY_PATH", "")


# ============================================================
# CLAUDE CODE GENERATOR
# ============================================================
def ask_claude(system: str, prompt: str,
               max_tokens: int = 8096) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    r      = client.messages.create(
        model      = "claude-sonnet-4-6",
        max_tokens = max_tokens,
        system     = system,
        messages   = [{"role": "user", "content": prompt}]
    )
    return r.content[0].text


def clean_code(code: str) -> str:
    import re
    code = re.sub(r'```[\w]*\n?', '', code)
    code = re.sub(r'```', '', code)
    return code.strip()


# ============================================================
# APP PLANNER
# ============================================================
def plan_app(prompt: str, app_type: str) -> dict:
    print(f"\n[BUILDER] Planning {app_type} app...")

    type_context = {
        "web"   : "FastAPI backend + HTML/JS frontend + MongoDB",
        "api"   : "FastAPI REST API + MongoDB + JWT auth",
        "bot"   : "Python bot + webhook + MongoDB",
        "full"  : "FastAPI + React + MongoDB + Docker"
    }.get(app_type, "FastAPI + MongoDB")

    raw = ask_claude(
        system = f"""You are a senior software architect.
Plan a {type_context} application.
Return ONLY valid JSON, no explanation.

JSON format:
{{
  "app_name": "snake_case_name",
  "title": "App Title",
  "description": "What it does",
  "app_type": "{app_type}",
  "port": 8000,
  "dependencies": ["fastapi", "uvicorn", "motor", "python-dotenv"],
  "files": [
    {{"name": "main.py", "description": "FastAPI entry point"}},
    {{"name": "database.py", "description": "MongoDB connection"}},
    {{"name": "models.py", "description": "Pydantic models"}},
    {{"name": "routes/api.py", "description": "API routes"}},
    {{"name": ".env.example", "description": "Environment variables"}},
    {{"name": "requirements.txt", "description": "Dependencies"}},
    {{"name": "Dockerfile", "description": "Docker config"}},
    {{"name": "docker-compose.yml", "description": "Docker compose"}}
  ],
  "features": ["feature1", "feature2"],
  "api_endpoints": [
    {{"method": "GET", "path": "/", "description": "Health check"}},
    {{"method": "POST", "path": "/api/items", "description": "Create item"}}
  ],
  "env_vars": ["MONGODB_URL", "SECRET_KEY", "PORT"],
  "run_command": "uvicorn main:app --reload"
}}""",
        prompt = f"Plan this {app_type} app: {prompt}"
    )

    try:
        import re
        text = re.sub(r'```json|```', '', raw).strip()
        return json.loads(text)
    except Exception:
        return {
            "app_name"    : "my_app",
            "title"       : prompt[:50],
            "description" : prompt,
            "app_type"    : app_type,
            "port"        : 8000,
            "dependencies": ["fastapi", "uvicorn", "motor", "python-dotenv"],
            "files"       : [
                {"name": "main.py",      "description": "Main app"},
                {"name": "database.py",  "description": "DB connection"},
                {"name": "models.py",    "description": "Data models"},
                {"name": "requirements.txt", "description": "Deps"},
                {"name": "Dockerfile",   "description": "Docker"},
            ],
            "features"    : [],
            "api_endpoints": [],
            "env_vars"    : ["MONGODB_URL", "SECRET_KEY"],
            "run_command" : "uvicorn main:app --reload"
        }


# ============================================================
# FILE GENERATORS PER TYPE
# ============================================================

def gen_main_py(plan: dict, prompt: str) -> str:
    app_type = plan.get("app_type", "api")
    endpoints = json.dumps(
        plan.get("api_endpoints", []), indent=2
    )

    return clean_code(ask_claude(
        system = """You are a senior FastAPI developer.
Write complete, production-ready FastAPI code.
Rules:
- No triple-quoted strings
- Complete error handling
- CORS enabled
- MongoDB with motor (async)
- Pydantic v2 models
- Indonesian comments
- Return ONLY Python code, no markdown""",
        prompt = f"""Write main.py for:
App: {plan['title']}
Type: {app_type}
Description: {plan['description']}
Endpoints: {endpoints}
Features: {plan.get('features', [])}
Original request: {prompt}

Include: FastAPI app, CORS, MongoDB connection, all routes, startup/shutdown events."""
    ))


def gen_database_py(plan: dict) -> str:
    return clean_code(ask_claude(
        system = """Write Python MongoDB connection code using motor (async).
No triple-quoted strings. Return ONLY Python code.""",
        prompt = f"""Write database.py for {plan['title']}.
Include: async MongoDB connection, get_database(), indexes, connection pooling.
Use motor and pymongo. MongoDB URL from environment variable."""
    ))


def gen_models_py(plan: dict, prompt: str) -> str:
    return clean_code(ask_claude(
        system = """Write Pydantic v2 models for FastAPI + MongoDB.
No triple-quoted strings. Return ONLY Python code.""",
        prompt = f"""Write models.py for: {prompt}
App: {plan['title']}
Features: {plan.get('features', [])}
Include: Request/Response models, MongoDB document models, validators."""
    ))


def gen_routes(plan: dict, prompt: str) -> str:
    endpoints = json.dumps(
        plan.get("api_endpoints", []), indent=2
    )
    return clean_code(ask_claude(
        system = """Write FastAPI router with full CRUD operations.
Use async/await. MongoDB with motor. No triple-quoted strings.
Return ONLY Python code.""",
        prompt = f"""Write API routes for: {prompt}
App: {plan['title']}
Endpoints: {endpoints}
Include: full CRUD, error handling, response models, MongoDB operations."""
    ))


def gen_requirements(plan: dict) -> str:
    deps = plan.get("dependencies", [
        "fastapi", "uvicorn", "motor", "pymongo",
        "python-dotenv", "pydantic"
    ])
    base = [
        "fastapi>=0.111.0",
        "uvicorn[standard]>=0.30.0",
        "motor>=3.3.0",
        "pymongo>=4.6.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "python-multipart>=0.0.9",
        "httpx>=0.27.0",
    ]
    extra = [
        d for d in deps
        if d not in [
            "fastapi", "uvicorn", "motor",
            "pymongo", "python-dotenv", "pydantic"
        ]
    ]
    return "\n".join(base + extra)


def gen_dockerfile(plan: dict) -> str:
    port = plan.get("port", 8000)
    return f"""FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {port}

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]"""


def gen_docker_compose(plan: dict) -> str:
    name = plan.get("app_name", "myapp")
    port = plan.get("port", 8000)
    return f"""version: '3.8'

services:
  app:
    build: .
    container_name: {name}
    ports:
      - "{port}:{port}"
    environment:
      - MONGODB_URL=mongodb://mongo:27017/{name}
      - SECRET_KEY=change-this-secret-key
      - PORT={port}
    depends_on:
      - mongo
    restart: unless-stopped
    volumes:
      - .:/app

  mongo:
    image: mongo:7
    container_name: {name}_mongo
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    restart: unless-stopped

volumes:
  mongo_data:"""


def gen_env_example(plan: dict) -> str:
    name = plan.get("app_name", "myapp")
    port = plan.get("port", 8000)
    lines = [
        f"MONGODB_URL=mongodb://localhost:27017/{name}",
        f"SECRET_KEY=your-secret-key-here",
        f"PORT={port}",
        f"APP_NAME={plan.get('title', name)}",
        f"DEBUG=True",
    ]
    for var in plan.get("env_vars", []):
        if var not in ["MONGODB_URL", "SECRET_KEY", "PORT"]:
            lines.append(f"{var}=")
    return "\n".join(lines)


def gen_readme(plan: dict, prompt: str) -> str:
    name  = plan.get("title", plan.get("app_name", "App"))
    port  = plan.get("port", 8000)
    feats = "\n".join(
        f"- {f}" for f in plan.get("features", [])
    )
    eps   = "\n".join(
        f"- {e['method']} {e['path']} — {e['description']}"
        for e in plan.get("api_endpoints", [])
    )
    return f"""# {name}

{plan.get('description', '')}

Built with PETER AI from prompt: "{prompt}"

## Tech Stack
- FastAPI + Python 3.12
- MongoDB + Motor (async)
- Docker + Docker Compose
- Deployed on VPS

## Features
{feats}

## API Endpoints
{eps}

## Quick Start (Local)
```bash