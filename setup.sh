#!/bin/bash

# Setup Script for LinkedIn Job Scraper
# This script helps you configure the application

echo "🚀 LinkedIn Job Scraper - Setup Wizard"
echo "======================================"
echo ""

# Check if .env already exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " overwrite
    if [[ ! $overwrite =~ ^[Yy]$ ]]; then
        echo "Setup cancelled. Using existing .env file."
        exit 0
    fi
fi

# Copy from example
if [ ! -f .env.example ]; then
    echo "❌ Error: .env.example not found!"
    exit 1
fi

echo "📋 Creating .env file from .env.example..."
cp .env.example .env

echo ""
echo "Now let's configure your credentials..."
echo ""

# Get LinkedIn email
read -p "Enter your LinkedIn email: " linkedin_email
if [ -z "$linkedin_email" ]; then
    echo "❌ Email cannot be empty!"
    exit 1
fi

# Get LinkedIn password
read -sp "Enter your LinkedIn password: " linkedin_password
echo ""
if [ -z "$linkedin_password" ]; then
    echo "❌ Password cannot be empty!"
    exit 1
fi

# Get Gemini API key
echo ""
echo "📝 Get your Gemini API key from: https://makersuite.google.com/app/apikey"
read -p "Enter your Gemini API key: " gemini_key
if [ -z "$gemini_key" ]; then
    echo "⚠️  Warning: No API key provided. CV generation will not work."
    gemini_key="your_google_api_key_here"
fi

# Update .env file
cat > .env << EOF
# LinkedIn Credentials
LINKEDIN_EMAIL=$linkedin_email
LINKEDIN_PASSWORD=$linkedin_password

# Browser Settings
HEADLESS=True

# Google Gemini API Key for CV Generation
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=$gemini_key
EOF

echo ""
echo "✅ Configuration complete!"
echo ""
echo "Your .env file has been created with your credentials."
echo ""
echo "⚠️  SECURITY NOTE:"
echo "   - Never share your .env file"
echo "   - Never commit it to Git (it's already in .gitignore)"
echo "   - Keep your credentials safe"
echo ""
echo "🎯 Next steps:"
echo "   1. Run: ./run_dev_server.sh"
echo "   2. Open: http://localhost:8080"
echo "   3. Start scraping jobs!"
echo ""
