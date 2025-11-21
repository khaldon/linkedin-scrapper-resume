# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project definition
COPY pyproject.toml .

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Download spaCy model (as root)
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Create necessary directories and set permissions
RUN mkdir -p data logs static && \
    chmod 777 data logs static

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user BEFORE installing Playwright browsers
USER appuser

# Install Playwright browsers as appuser (so they're accessible)
RUN playwright install chromium

# Expose port 7860 (Hugging Face default)
EXPOSE 7860

# Set environment variables
ENV PORT=7860
ENV PYTHONUNBUFFERED=1
ENV DATABASE_PATH=/app/data/jobs.db

# Run the application
CMD exec uvicorn api:app --host 0.0.0.0 --port ${PORT} --workers 1
