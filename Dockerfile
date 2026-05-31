FROM python:3.14-slim AS css-builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY tailwind/ tailwind/
COPY app/static/ app/static/
COPY app/templates/ app/templates/
RUN uv run tailwindcss-extra -i tailwind/input.css -o app/static/css/app.css --minify

FROM python:3.14-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY app/ app/
COPY migrations/ migrations/
COPY alembic.ini entrypoint.sh ./
COPY --from=css-builder /app/app/static/css/app.css app/static/css/app.css
RUN chmod +x entrypoint.sh
EXPOSE 8000
CMD ["./entrypoint.sh"]
