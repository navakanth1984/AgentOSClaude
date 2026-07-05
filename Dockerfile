# --- Stage 1: Build dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: Final runtime image ---
FROM python:3.11-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

COPY agent_os/ ./agent_os/
COPY tests/ ./tests/
COPY *.py ./
COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh

# Persist runs, models, and qualification results
VOLUME ["/app/jobs", "/app/models", "/app/qualification_runs"]

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "agent_os.speech.api:app", "--host", "0.0.0.0", "--port", "8000"]
