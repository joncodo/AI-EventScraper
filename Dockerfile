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
RUN pip install --no-cache-dir -r requirements-railway.txt

# Install critical dependencies with multiple fallback methods
RUN pip install --no-cache-dir feedparser==6.0.10 icalendar==5.0.11 || \
    pip install --no-cache-dir --force-reinstall feedparser icalendar || \
    pip install --no-cache-dir --no-deps feedparser icalendar || \
    pip install --no-cache-dir sgmllib3k python-dateutil pytz lxml || \
    echo "Some dependencies may need runtime installation"

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

# Default command - run startup deps check, test, then main app
CMD ["sh", "-c", "echo 'Starting startup sequence...' && python startup_deps.py && echo 'Deps check complete, running startup test...' && python test_startup.py && echo 'Startup test complete, starting main app...' && python railway_complete.py"]
