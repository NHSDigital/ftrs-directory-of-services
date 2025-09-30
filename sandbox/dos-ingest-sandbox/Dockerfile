FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN pip install --trusted-host pypi.python.org \
                --trusted-host pypi.org \
                --trusted-host files.pythonhosted.org \
                --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root --no-ansi

COPY src /app/src

EXPOSE 9000

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "9000"]
