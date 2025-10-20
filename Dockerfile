# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-railway.txt .

# Install Python dependencies with multiple methods for critical packages
RUN echo "🔍 Installing Python dependencies..." && \
    pip install --no-cache-dir -r requirements-railway.txt && \
    echo "✅ Main dependencies installed"

# Install critical dependencies with multiple fallback methods
RUN echo "🔍 Installing critical dependencies..." && \
    (pip install --no-cache-dir atoma==0.0.12 icalendar==5.0.11 || \
     pip install --no-cache-dir --force-reinstall atoma icalendar || \
     pip install --no-cache-dir --no-deps atoma icalendar || \
     pip install --no-cache-dir python-dateutil pytz lxml || \
     echo "⚠️ Some dependencies may need runtime installation") && \
    echo "✅ Critical dependencies installation attempt completed"

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port (Railway uses PORT env var)
EXPOSE 8080

# Health check with longer startup time
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=5 \
    CMD curl -f http://localhost:8080/ping || exit 1

# Default command - simple server test
CMD ["python", "simple_server_test.py"]
