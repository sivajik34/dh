# =============================
# Stage 1: Builder
# =============================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install only what’s needed to build wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

# =============================
# Stage 2: Runtime
# =============================
FROM python:3.11-slim

WORKDIR /app

# Copy built wheels and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy source code
COPY . .

EXPOSE 8007

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8007"]
