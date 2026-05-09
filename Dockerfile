# BUILD STAGE
FROM python:3.14.4-slim-bookworm AS builder

WORKDIR /app

# Create virtual environment
RUN python -m venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

# Install dependencies first (cached if unchanged)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . ./

# PRODUCTION STAGE
FROM python:3.14.4-slim-bookworm

WORKDIR /app

# Run as non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Copy app and dependencies from builder stage
COPY --from=builder --chown=appuser:appuser /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# exec replaces shell so fastapi receives SIGTERM for clean shutdown
CMD ["/bin/sh", "-c", "exec fastapi run --host 0.0.0.0 --port \"$PORT\" --proxy-headers --forwarded-allow-ips '*'"]
