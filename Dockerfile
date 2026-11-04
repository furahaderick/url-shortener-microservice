# Stage 1: Builder
FROM python:3.12-slim AS builder

# Install build tools and hiredis development headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libhiredis-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

# Configure poetry to not create a dedicated venv since a container is already isolated
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

COPY app/ ./app/

# Stage 2: Production
FROM python:3.12-slim AS production

# Install ONLY the runtime shared library for hiredis
RUN apt-get update && apt-get install -y --no-install-recommends \
    libhiredis1.1.0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages \
    /usr/local/lib/python3.12/site-packages

# Copy installed executable scripts
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY --from=builder /app/app ./app

EXPOSE 8000

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]
