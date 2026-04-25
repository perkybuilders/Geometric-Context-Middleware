# syntax=docker/dockerfile:1
FROM python:3.11-slim as base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Local development stage
FROM base as local
# Volume mount will override /app
CMD ["python", "cli.py"]

# Production stage
FROM base as production
# Create non-root user
RUN adduser --disabled-password --gecos "" appuser
# Copy source code
COPY . .
# Create a data directory and give permissions to appuser
RUN mkdir -p /app/data && chown -R appuser:appuser /app
# Switch to non-root user
USER appuser
CMD ["python", "cli.py"]
