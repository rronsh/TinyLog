# TinyLog

A lightweight baby tracking app for logging feedings and sleep sessions. Built as a progressive web app (PWA) with a clean mobile-first UI.

## Features

- **Feedings** — log breast (left/right/both with per-side timers) and bottle feeds (amount in ml)
- **Sleep** — start/stop sleep sessions with duration tracking
- **Multiple babies** — all data is scoped per baby
- **HTMX-powered UI** — partial page updates without a JS framework
- **REST API** — full JSON API at `/api/v1` for all resources
- **Offline-ready** — service worker for basic offline support

## Stack

- **FastAPI** + **SQLModel** + **SQLite** — Python backend with sync SQLite
- **Alembic** — database migrations (run automatically on startup)
- **Jinja2** + **HTMX** — server-rendered HTML with dynamic partials
- **Tailwind CSS** — compiled via `pytailwindcss-extra`
- **uv** — dependency management

## Getting started

```bash
# Install dependencies and download htmx
make install

# Build CSS once
make css

# Start the dev server
make dev
```

The app will be available at `http://localhost:8000`.

Copy `.env.example` to `.env` to customize the database path:

```
DATABASE_URL=sqlite:///./data/tinylog.db
```

## Development

```bash
make css-watch   # rebuild CSS on file changes
make test        # run full test suite
make lint        # ruff check
make fmt         # ruff format
make typecheck   # ty check
```

Run a single test file:

```bash
uv run pytest -v tests/test_api_babies.py
uv run pytest -v -k "test_name"
```

## Database migrations

Migrations are managed with Alembic and run automatically when the app starts. To generate a migration after changing a model:

```bash
make migration msg="add weight column"
```

To apply migrations manually:

```bash
make migrate
```

## API

The REST API is mounted at `/api/v1`. All IDs are UUID v7.

| Method | Path | Description |
|--------|------|-------------|
| `GET/POST` | `/api/v1/babies` | List or create babies |
| `GET/PATCH/DELETE` | `/api/v1/babies/{id}` | Get, update, or delete a baby |
| `GET/POST` | `/api/v1/babies/{id}/feedings` | List or log a feeding |
| `GET/PATCH/DELETE` | `/api/v1/babies/{id}/feedings/{id}` | Manage a feeding |
| `GET/POST` | `/api/v1/babies/{id}/sleeps` | List or start a sleep session |
| `POST` | `/api/v1/babies/{id}/sleeps/{id}/end` | End an active sleep session |
| `GET/PATCH/DELETE` | `/api/v1/babies/{id}/sleeps/{id}` | Manage a sleep session |

Interactive docs: `http://localhost:8000/docs`

## Deployment

Container images are built and published to `ghcr.io` automatically on every push to `main` via GitHub Actions.

### Podman quadlet

The `deploy/` directory contains a systemd quadlet unit for running TinyLog as a Podman container. Copy the files to your systemd unit directory and enable the service:

```bash
cp deploy/tinylog.container ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user start tinylog
```

The container mounts `/mnt/data/app_data/tinylog` for persistent SQLite storage. Migrations run automatically on startup, so deploying an update is just:

```bash
podman pull ghcr.io/your-username/tinylog:latest
systemctl --user restart tinylog
```

### Build locally

```bash
make build                        # build with Podman (default)
make build CONTAINER_TOOL=docker  # build with Docker
```

## Project layout

```
app/
  main.py              # FastAPI app, lifespan, router mounts
  config.py            # Settings (DATABASE_URL via .env)
  database.py          # Sync engine + get_session dependency
  templates_config.py  # Shared Jinja2 instance + custom filters
  models/              # SQLModel table + Create/Update schemas
  routers/
    api/               # JSON REST API (/api/v1)
    views/             # HTML view routes
  services/            # Business logic (feedings, sleeps, babies)
  templates/           # Jinja2 templates + partials + components
  static/              # CSS, JS (htmx), icons, service worker
migrations/            # Alembic migration versions
deploy/                # Podman quadlet unit files
tests/                 # pytest suite (in-memory SQLite)
tailwind/              # Tailwind CSS input
```
