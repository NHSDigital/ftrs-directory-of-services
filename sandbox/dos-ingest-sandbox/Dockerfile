FROM python:3.12-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root --no-ansi

COPY src /app/src

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9000/_status || exit 1

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "9000"]
