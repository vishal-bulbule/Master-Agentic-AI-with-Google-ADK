# Author: Vishal Bulbule
# Date: 2026-09-22

# Custom image for ADK agents that need more than the image `adk deploy`
# generates. Here the extra is Node.js, so an agent can start stdio MCP servers
# with `npx`.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# nodejs and npm: run stdio MCP servers with npx.
# ca-certificates: TLS to external APIs.
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies first, so code changes do not invalidate this layer.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
COPY agents/ agents/

RUN useradd --create-home --uid 1000 app && chown -R app:app /app
USER app

# Cloud Run sets PORT at runtime. 8080 is the default for local `docker run`.
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
