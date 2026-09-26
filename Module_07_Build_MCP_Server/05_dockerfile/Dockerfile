# Author: Vishal Bulbule
# Date: 2026-09-22

FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so this layer is cached across code edits.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

# Cloud Run sets PORT at runtime; 8080 is the default for local docker run.
ENV PORT=8080
EXPOSE 8080

# Run as a non-root user.
RUN useradd --create-home appuser
USER appuser

CMD ["python", "server.py"]
