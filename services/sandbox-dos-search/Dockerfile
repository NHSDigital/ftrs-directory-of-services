FROM python:3.12-slim

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install curl for healthcheck and create non-root user
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy dependency manifest and readme (required by hatchling build backend)
COPY pyproject.toml README.md /app/

# Install only production dependencies (no dev group)
RUN uv pip install --system --no-cache .

# Copy application code
COPY src /app/src

# Permissions
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:9000/_status || exit 1

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "9000"]
