FROM python:3.12.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.10.7 /uv /usr/local/bin/uv

RUN addgroup --system --gid 1001 appgroup \
 && adduser --system --uid 1001 --gid 1001 appuser

WORKDIR /app

COPY pyproject.toml uv.lock .
RUN uv sync --no-dev --frozen

COPY . .
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

CMD [".venv/bin/python", "server.py"]
