# Use corresponding python version stored in the '.tool-versions' file
FROM python:3.12.7

# Create a non-root user and switch to it
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

# Add a simple healthcheck (e.g., checking Python is available)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python --version || exit 1
