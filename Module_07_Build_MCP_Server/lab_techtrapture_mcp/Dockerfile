# Author: Vishal Bulbule
# Date: 2026-09-22

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# server_http.py imports the server definition from server_stdio.py.
COPY courses.py server_stdio.py server_http.py ./

# Cloud Run sets PORT at runtime; 8080 is the default for local docker run.
ENV PORT=8080
EXPOSE 8080

RUN useradd --create-home appuser
USER appuser

CMD ["python", "server_http.py"]
