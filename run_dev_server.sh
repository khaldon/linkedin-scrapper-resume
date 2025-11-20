#!/bin/bash

# Local Development Server Script
# This script runs the application locally for testing before deployment

echo "🚀 Starting LinkedIn Job Scraper - Local Development Server"
echo "============================================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env with your credentials before continuing."
    echo ""
    read -p "Press Enter when ready..."
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "📦 Activating virtual environment..."
    source .venv/bin/activate 2>/dev/null || {
        echo "❌ Virtual environment not found. Please run: uv sync"
        exit 1
    }
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data logs static

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
python -c "import fastapi" 2>/dev/null || {
    echo "❌ FastAPI not installed. Installing dependencies..."
    uv sync
}

# Check if spaCy model is downloaded
echo "🔍 Checking spaCy model..."
python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null || {
    echo "📥 Downloading spaCy model..."
    python -m spacy download en_core_web_sm
}

# Install Playwright browsers if needed
echo "🔍 Checking Playwright browsers..."
playwright install chromium 2>/dev/null || {
    echo "📥 Installing Playwright browsers..."
    playwright install chromium
}

echo ""
echo "✅ All checks passed!"
echo ""
echo "🌐 Starting server on http://localhost:8080"
echo "📊 API docs available at http://localhost:8080/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the server
uvicorn api:app --host 0.0.0.0 --port 8080 --reload
