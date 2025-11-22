# CareerBoost AI - Backend

This is the backend API for CareerBoost AI, a LinkedIn Job Scraper & CV Tailor.

## 🚀 Deployment

This backend is deployed to **Hugging Face Spaces**.

### Prerequisites

- Hugging Face account
- Git configured with Hugging Face credentials
- Environment variables set in Hugging Face Spaces secrets

### Deploy to Hugging Face Spaces

From the **root directory** of the project:

```bash
git push space main
```

The Dockerfile in the root will automatically build from the `backend/` directory.

## 🔧 Environment Variables

Set these in your Hugging Face Space settings (Settings → Variables and secrets):

### Required
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/public key
- `GOOGLE_API_KEY`: Google Gemini API key for CV generation
- `FIREBASE_SERVICE_ACCOUNT_JSON`: Firebase Admin SDK credentials (JSON content)

### Optional
- `HEADLESS`: Browser headless mode (default: `True`)
- `PORT`: Server port (default: `7860`)

## 📁 Structure

```
backend/
├── api.py                  # FastAPI application
├── src/
│   ├── scraper.py         # LinkedIn job scraper
│   ├── database.py        # Supabase integration
│   ├── llm_generator.py   # AI CV generation
│   ├── stats_generator.py # Job market analytics
│   ├── firebase_auth.py   # Firebase authentication
│   └── ...
├── data/                  # Generated CVs, charts, reports
├── logs/                  # Application logs
├── tests/                 # Unit tests
├── Dockerfile             # Docker configuration
├── pyproject.toml         # Python dependencies
└── verify_setup.py        # Environment verification script
```

## 🔐 Authentication

The backend uses **Firebase Admin SDK** to verify tokens from the frontend:
- Users authenticate via Firebase Auth (Google OAuth2) on the frontend
- Frontend sends Firebase ID token in `Authorization: Bearer <token>` header
- Backend verifies token using Firebase Admin SDK

## 🌐 API Endpoints

### Public
- `GET /`: API information
- `GET /api/health`: Health check

### Authenticated
- `POST /api/scrape`: Scrape a LinkedIn job posting
- `POST /api/generate-cv`: Generate tailored CV
- `GET /api/jobs`: Get user's scraped jobs
- `GET /api/stats`: Get job market statistics
- `POST /api/stats/generate`: Generate fresh statistics

## 🛠️ Local Development

1. **Set up environment**:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your credentials
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Verify setup**:
   ```bash
   uv run python verify_setup.py
   ```

4. **Run the server**:
   ```bash
   uv run uvicorn api:app --reload --port 8080
   ```

5. **Access API docs**:
   - Swagger UI: http://localhost:8080/docs
   - ReDoc: http://localhost:8080/redoc

## 🧪 Testing

```bash
cd backend
uv run pytest tests/
```

## 📊 Database

The backend uses **Supabase** (PostgreSQL) for data storage:
- Jobs table: Scraped job postings
- Users table: User accounts (synced from Firebase)
- Generated CVs: Tailored CVs for each job

## 🤖 AI Integration

- **Google Gemini API**: Used for CV generation and market insights
- **spaCy**: NLP for skill extraction and analysis
- **scikit-learn**: TF-IDF for keyword analysis

## 📄 License

MIT License - See LICENSE file in the root directory
