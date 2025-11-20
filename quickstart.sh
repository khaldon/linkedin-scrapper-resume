#!/bin/bash

# Quick Start Script for OAuth2 Setup
# This script helps you get started quickly

echo "🚀 CareerBoost AI - OAuth2 Quick Start"
echo "======================================"
echo ""

echo "📋 Checklist:"
echo ""
echo "Before running this app, you need to:"
echo ""
echo "1. ✅ Create Firebase Project"
echo "   - Go to: https://console.firebase.google.com/"
echo "   - Create a new project"
echo ""
echo "2. ✅ Enable Google Sign-In"
echo "   - Firebase Console → Authentication → Sign-in method"
echo "   - Enable 'Google'"
echo ""
echo "3. ✅ Get Firebase Config"
echo "   - Firebase Console → Project Settings → Your apps → Web"
echo "   - Copy the config object"
echo ""
echo "4. ✅ Update static/app.js"
echo "   - Replace firebaseConfig with your config"
echo ""
echo "5. ✅ (Optional) Enable LinkedIn Sign-In"
echo "   - Get OAuth credentials from LinkedIn Developers"
echo "   - Add OpenID Connect provider in Firebase"
echo ""

read -p "Have you completed all the steps above? (y/N): " ready

if [[ ! $ready =~ ^[Yy]$ ]]; then
    echo ""
    echo "⚠️  Please complete the setup steps first!"
    echo "📖 Read FIREBASE_SETUP.md for detailed instructions"
    echo ""
    exit 0
fi

echo ""
echo "🔧 Starting development server..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "📝 Please edit .env and add your credentials:"
    echo "   - LINKEDIN_EMAIL (optional, can use OAuth2 stored credentials)"
    echo "   - LINKEDIN_PASSWORD (optional)"
    echo "   - GOOGLE_API_KEY (for CV generation)"
    echo ""
    read -p "Press Enter to continue..."
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Download spaCy model
echo "📥 Downloading spaCy model..."
uv run python -m spacy download en_core_web_sm

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
uv run playwright install chromium

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting server on http://localhost:8080"
echo ""
echo "📝 Next steps:"
echo "   1. Open http://localhost:8080 in your browser"
echo "   2. Click 'Login' and try OAuth2 sign-in"
echo "   3. Store your LinkedIn credentials (encrypted)"
echo "   4. Start scraping jobs!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uv run uvicorn api:app --host 0.0.0.0 --port 8080 --reload
