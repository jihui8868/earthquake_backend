# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Earthquake Backend — a FastAPI async web service for an earthquake-related knowledge management platform. Uses PostgreSQL (via asyncpg + SQLAlchemy async) with auto-table-creation on startup.

## Commands

```bash
# Run dev server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Install dependencies
uv sync

# Add a dependency
uv add <package>

# Quick import check (no DB needed)
uv run python -c "from app.main import app; print('OK')"
```

No test framework is configured yet.

## Architecture

Three-layer structure: **Router → CRUD → Model**, all async.

- `app/main.py` — FastAPI app with lifespan that auto-creates all tables via `Base.metadata.create_all`
- `app/core/config.py` — `pydantic-settings` config (reads `.env`), exposes `settings` singleton
- `app/core/database.py` — async SQLAlchemy engine, `async_session` factory, `Base` declarative base, `get_db` dependency
- `app/models/` — SQLAlchemy ORM models (UUID string PKs, `server_default=func.now()` timestamps)
- `app/crud/` — Pure DB operations; each module receives `AsyncSession` as first arg, returns model instances
- `app/router/` — HTTP layer only: request parsing, calling crud, converting to response schemas
- `app/schemas/` — Pydantic models for request/response; use camelCase field names to match frontend

All routers are mounted under `/api` prefix in `main.py`. The frontend expects responses wrapped in `ResponseModel(code, message, data)`.

## Key Conventions

- **Field naming**: DB models use snake_case (`parent_id`), schemas use camelCase (`parentId`) to match the Vue frontend
- **IDs**: All primary keys are `String(36)` UUIDs generated via `uuid.uuid4()`
- **Tree structures**: Department, Permission, KnowledgeBaseCategory, and FileItem use self-referential `parent_id` FKs; tree-building happens in router layer
- **Database config**: Defaults in `config.py`, overridable via `.env` or environment variables (`DATABASE_HOST`, `DATABASE_PORT`, etc.)
- **File uploads**: Stored under `settings.UPLOAD_DIR` (default: `uploads/`); DB records track the file path
