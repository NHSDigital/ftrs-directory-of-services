FROM python:3.12-slim

# Install curl for healthcheck
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy dependency manifests
COPY pyproject.toml poetry.lock /app/

# Install poetry and project dependencies (no virtualenv)
RUN pip install --no-cache-dir "poetry>=2,<3" \
    && poetry config virtualenvs.create false \
    && (poetry check --lock || poetry lock --no-interaction --no-ansi) \
    && poetry install --no-interaction --no-root --no-ansi

# Copy application code
COPY src /app/src

# Permissions
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:9000/_status || exit 1

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "9000"]
