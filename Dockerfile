# ==============================================================================
# STAGE 1: BUILD ENGINE & DEPENDENCY COMPILATION
# ==============================================================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Install compilation essentials needed for wheel processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Compile dependencies directly to a clean wheels directory
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==============================================================================
# STAGE 2: LEAN COMPLIANT PRODUCTION RUNTIME Environment
# ==============================================================================
FROM python:3.10-slim AS runner

WORKDIR /app

# Establish strict enterprise compliance environment flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Expose microservice interface network matrix
EXPOSE 8000

# Create an unprivileged application user and group
RUN groupadd -g 10001 mlgroup && \
    useradd -u 10001 -g mlgroup -m -s /bin/bash mluser

# Extract pre-compiled library modules from builder phase safely
COPY --from=builder /root/.local /home/mluser/.local
ENV PATH=/home/mluser/.local/bin:$PATH

# Transfer application components and configurations
COPY --chown=mluser:mlgroup config/ ./config/
COPY --chown=mluser:mlgroup data_pipeline/ ./data_pipeline/
COPY --chown=mluser:mlgroup src/ ./src/
COPY --chown=mluser:mlgroup legal/ ./legal/

# Assign immutable folder workspace boundaries to application runner
RUN mkdir -p models && chown -R mluser:mlgroup /app

# Drop root execution privileges and assume unprivileged identity context
USER 10001

# Run health probes locally to verify infrastructure stability
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Launch production microservice engine via Uvicorn ASGI routing
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]

