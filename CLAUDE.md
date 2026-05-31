# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
make install       # install deps + download htmx
make dev           # build CSS then start uvicorn (do NOT run this; user starts server themselves)
make css           # build minified CSS once
make css-watch     # rebuild CSS on file changes
make test          # run full test suite
uv run pytest -v tests/test_api_babies.py   # run a single test file
uv run pytest -v -k "test_name"             # run a single test by name
```

> Never start or kill the uvicorn server — the user runs it themselves.

## Stack

- **FastAPI** with async SQLite via **SQLModel** + **aiosqlite**
- **Jinja2** templates with **HTMX** for partial page updates
- **Tailwind CSS** compiled via `pytailwindcss-extra` from `tailwind/input.css` → `app/static/css/app.css`
- **uv** for dependency management (`pyproject.toml`)
- PKs are **UUID v7** (`uuid7()` from the `uuid` package)

## Architecture

The app has two parallel router trees mounted in `app/main.py`:

- `app/routers/api/` — JSON REST API at `/api/v1` (babies, feedings, sleeps)
- `app/routers/views/` — HTML view routes that render Jinja2 templates

View routes check `HX-Request` headers to return HTMX partials vs. full redirects. Partials live in `app/templates/partials/`. Reusable UI pieces are in `app/templates/components/` (macros, sheet drawer, dock, header, confirm modal).

**Session injection:** `app/database.py` exports `get_session` — an async generator used as a FastAPI dependency throughout both router trees.

**Template filters:** `app/templates_config.py` defines the shared `templates` instance and registers two Jinja2 filters: `| duration` (seconds → human string) and `| relative` (datetime → "Xm ago").

**Models** follow the SQLModel pattern: one `table=True` class (the DB model) plus `Create` and `Update` variants without the primary key.

## Testing

Tests use an in-memory SQLite database. `tests/conftest.py` sets up three async fixtures (`engine` → `session` → `client`) and overrides `get_session` via `app.dependency_overrides`. `asyncio_mode = "auto"` is set globally so no `@pytest.mark.asyncio` decorators are needed.

## Configuration

`app/config.py` reads settings from `.env` via `pydantic-settings`. The only setting is `DATABASE_URL` (default: `sqlite+aiosqlite:///./data/tinylog.db`). The `data/` directory is created at startup in the lifespan handler.
