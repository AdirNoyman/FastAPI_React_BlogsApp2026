# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI blog application (part of Corey Schafer's FastAPI BootCamp 2026). Currently a single-file app with in-memory data, Jinja2 templates, and JSON API endpoints.

## Important

- Always use `uv` for package management. Never use `pip`.

## Commands

```bash
# Install dependencies
uv sync

# Run dev server with hot reload
uvicorn main:app --reload

# Run via FastAPI CLI
fastapi run main.py
```

No test framework is currently configured.

## Architecture

Single-file FastAPI app (`main.py`) with:

- **In-memory data store**: Posts stored as a list of dicts (no database yet)
- **Server-side rendering**: Jinja2 templates in `templates/` for HTML responses
- **JSON API**: Separate `/api/posts` endpoint returning raw JSON
- **Dual routes**: `GET /` and `GET /posts` serve the same HTML template; `GET /api/posts` serves JSON

**Data flow**: Request → route handler → reads from in-memory list → renders template (HTML) or returns dict (JSON)

## Key URLs (when running locally)

- `/` or `/posts` — HTML blog listing
- `/api/posts` — JSON posts endpoint
- `/docs` — Swagger UI (auto-generated)

## Tech Stack

- **Python 3.14**, managed with **uv**
- **FastAPI** with Jinja2Templates for SSR
- **Uvicorn** as the ASGI server
