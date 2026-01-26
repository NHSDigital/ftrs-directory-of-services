# syntax=docker/dockerfile:1

############################
# Base OS layer
############################
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

############################
# Dependency builder (default: no corporate CA)
############################
FROM base AS deps

WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

############################
# Dependency builder (opt-in: corporate CA)
############################
FROM base AS deps-with-corp-ca

ARG CORP_CA_PEM=corp-proxy-ca.pem
WORKDIR /app

COPY ${CORP_CA_PEM} /usr/local/share/ca-certificates/corp-proxy.crt
RUN update-ca-certificates

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

############################
# Base runtime (no deps copied yet)
############################
FROM base AS runtime-base

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

WORKDIR /app

# Copy application code (avoid a recursive chown by using COPY --chown)
COPY --chown=appuser:appuser src /app/src

USER appuser

EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -fsS http://localhost:9000/_status || exit 1

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "9000"]

############################
# Runtime image (opt-in: corporate CA)
############################
FROM runtime-base AS runtime-with-corp-ca
COPY --from=deps-with-corp-ca ${VIRTUAL_ENV} ${VIRTUAL_ENV}

############################
# Runtime image (default)
############################
FROM runtime-base AS runtime
COPY --from=deps ${VIRTUAL_ENV} ${VIRTUAL_ENV}
