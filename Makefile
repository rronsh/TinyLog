.PHONY: install dev css css-watch test lint fmt typecheck migrate migration build compose-up

install:
	uv sync
	mkdir -p app/static/js app/static/css app/static/icons
	@if [ ! -f app/static/js/htmx.min.js ]; then \
	  curl -sL https://unpkg.com/htmx.org@2/dist/htmx.min.js -o app/static/js/htmx.min.js; \
	fi
	git config core.hooksPath .githooks
	chmod +x .githooks/pre-commit

lint:
	uv run ruff check .

fmt:
	uv run ruff format .

typecheck:
	uv run ty check app/

dev:
	mkdir -p app/static/css data
	uv run tailwindcss-extra -i tailwind/input.css -o app/static/css/app.css
	uv run alembic upgrade head
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

css:
	uv run tailwindcss-extra -i tailwind/input.css -o app/static/css/app.css --minify

css-watch:
	uv run tailwindcss-extra -i tailwind/input.css -o app/static/css/app.css --watch

test:
	uv run pytest -v

migrate:
	uv run alembic upgrade head

migration:
	uv run alembic revision --autogenerate -m "$(msg)"

CONTAINER_TOOL ?= podman

build:
	$(CONTAINER_TOOL) build -t tinylog .

compose-up:
	$(CONTAINER_TOOL) compose up -d
