FROM python:3.12-slim



# Install curl for healthcheck and create non-root user
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser \
    && useradd -r -g appuser appuser

WORKDIR /app

# Copy dependency manifests
COPY pyproject.toml poetry.lock /app/

# Install poetry and project dependencies (no virtualenv)
RUN pip install --no-cache-dir "poetry>=2,<3" \
    && poetry config virtualenvs.create false \
    && (poetry check --lock || poetry lock --no-interaction --no-ansi) \
    && poetry install --no-interaction --no-root --no-ansi

# Copy application code as root and make non-writable, then assign ownership and ensure non-writable
COPY --chown=root:root --chmod=0555 src /app/src
RUN chown -R appuser:appuser /app/src \
    && chmod -R a-w /app/src

USER appuser

EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:9000/_status || exit 1

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "9000"]
