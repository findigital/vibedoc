# VibeDoc SaaS Application - Docker Configuration
# Full-featured SaaS with authentication, subscriptions, and API
FROM python:3.11-slim

# Application labels
LABEL name="VibeDoc SaaS Application"
LABEL description="AI-powered Product Manager & Architect - SaaS Edition"
LABEL version="3.0.0"
LABEL maintainer="VibeDoc Team"

# Set working directory
WORKDIR /app

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV ENVIRONMENT=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose ports (Web: 7860, API: 8000)
EXPOSE 7860 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Default command - runs the SaaS web app
# For API server, override with: CMD ["python", "api.py"]
CMD ["python", "saas_app.py"]