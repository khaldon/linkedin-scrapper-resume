# CareerBoost AI - LinkedIn Job Scraper & CV Tailor

> 🚀 Scrape LinkedIn jobs anonymously, generate ATS-optimized CVs with AI, and analyze job market trends.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

## 📋 Overview

CareerBoost AI is a full-stack application that helps job seekers:
- **Scrape LinkedIn jobs** anonymously without requiring LinkedIn credentials
- **Generate tailored CVs** optimized for ATS (Applicant Tracking Systems) using Google Gemini AI
- **Analyze job market trends** to discover in-demand skills and technologies

## 🏗️ Architecture

This project is structured as a **monorepo** with separate frontend and backend:

```
playwright-scraper/
├── frontend/          # Firebase Hosting (Static Web App)
│   ├── static/       # HTML, JS, CSS
│   ├── firebase.json
│   └── README.md
├── backend/          # Hugging Face Spaces (FastAPI)
│   ├── api.py
│   ├── src/
│   ├── Dockerfile
│   └── README.md
├── Dockerfile        # Root Dockerfile (builds from backend/)
└── README.md         # This file
```

### Frontend
- **Hosting**: Firebase Hosting
- **Tech**: HTML, JavaScript, CSS
- **Auth**: Firebase Authentication (Google OAuth2)
- **Deployment**: `cd frontend && firebase deploy`

### Backend
- **Hosting**: Hugging Face Spaces
- **Tech**: FastAPI, Python 3.12, Playwright, spaCy
- **Database**: Supabase (PostgreSQL)
- **AI**: Google Gemini API
- **Deployment**: `git push space main` (from root)

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Firebase CLI: `npm install -g firebase-tools`
- Git configured for Hugging Face Spaces
- Supabase account
- Google Gemini API key
- Firebase project with Authentication enabled

### 1. Clone the Repository

```bash
git clone https://github.com/khaldon/linkedin-scrapper-resume.git
cd linkedin-scrapper-resume
```

### 2. Backend Setup

```bash
cd backend
cp .env.example .env
# Edit .env with your credentials
uv sync
uv run python verify_setup.py
uv run uvicorn api:app --reload --port 8080
```

See [backend/README.md](backend/README.md) for detailed instructions.

### 3. Frontend Setup

```bash
cd frontend
# Update static/config.js with your backend URL
firebase login
firebase deploy
```

See [frontend/README.md](frontend/README.md) for detailed instructions.

## 🔐 Authentication Flow

1. **User** signs in with Google on the frontend (Firebase Auth)
2. **Frontend** receives Firebase ID token
3. **Frontend** sends token in `Authorization: Bearer <token>` header to backend
4. **Backend** verifies token using Firebase Admin SDK
5. **Backend** processes request and returns data

## 🌟 Features

### 📊 Job Scraping
- Anonymous LinkedIn scraping (no login required)
- Extracts job title, company, description, poster info
- Stores in Supabase database

### 🤖 AI-Powered CV Generation
- Tailors your CV to specific job descriptions
- ATS optimization for better applicant tracking
- Generates both Markdown and PDF formats
- Uses Google Gemini for intelligent content generation

### 📈 Market Analytics
- Identifies top technologies and programming languages
- Analyzes soft and hard skills demand
- Generates visual charts and reports
- Provides AI-powered market insights

## 🛠️ Tech Stack

### Frontend
- HTML5, CSS3, JavaScript (ES6+)
- Firebase Authentication
- Firebase Hosting

### Backend
- **Framework**: FastAPI
- **Web Scraping**: Playwright
- **NLP**: spaCy, scikit-learn
- **AI**: Google Gemini API
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Firebase Admin SDK
- **PDF Generation**: WeasyPrint
- **Deployment**: Docker, Hugging Face Spaces

## 📦 Deployment

### Deploy Backend to Hugging Face Spaces

```bash
# From root directory
git push space main
```

**Environment Variables** (set in HF Spaces settings):
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `GOOGLE_API_KEY`
- `FIREBASE_SERVICE_ACCOUNT_JSON`

### Deploy Frontend to Firebase

```bash
cd frontend
firebase deploy
```

## 🧪 Testing

```bash
cd backend
uv run pytest tests/
```

## 📝 Environment Variables

See [backend/.env.example](backend/.env.example) for a complete list of required and optional environment variables.

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) for web scraping
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Google Gemini](https://ai.google.dev/) for AI-powered CV generation
- [Supabase](https://supabase.com/) for database hosting
- [Firebase](https://firebase.google.com/) for authentication and hosting
- [Hugging Face](https://huggingface.co/) for backend hosting

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ by [Khaldon](https://github.com/khaldon)**
