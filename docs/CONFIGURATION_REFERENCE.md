# Quick Configuration Reference

## ✅ Checklist for Production Deployment

### 1. Database Setup (Supabase)
- [ ] Create Supabase account at [supabase.com](https://supabase.com)
- [ ] Create new project
- [ ] Copy connection string from Settings → Database
- [ ] Add to `.env` or HF Secrets as `SUPABASE_DATABASE_URL`

### 2. API Keys
- [ ] Get Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- [ ] Add to `.env` or HF Secrets as `GOOGLE_API_KEY`

### 3. Hugging Face Spaces
- [ ] Create Space at [huggingface.co/new-space](https://huggingface.co/new-space)
- [ ] Select Docker SDK
- [ ] Add secrets in Settings → Repository secrets
- [ ] Push code to HF repository

### 4. Verification
- [ ] Run `uv run python verify_setup.py`
- [ ] All checks should pass ✅

---

## Environment Variables Quick Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_DATABASE_URL` | Recommended | - | PostgreSQL connection string |
| `GOOGLE_API_KEY` | **Yes** | - | Google Gemini API key |
| `DATABASE_PATH` | No | `data/jobs.db` | SQLite path (fallback) |
| `HEADLESS` | No | `True` | Browser headless mode |
| `PORT` | No | `7860` | Server port |
| `LINKEDIN_EMAIL` | No | - | LinkedIn credentials (optional) |
| `LINKEDIN_PASSWORD` | No | - | LinkedIn credentials (optional) |

---

## Connection Strings Format

### Supabase PostgreSQL
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

**Example:**
```
postgresql://postgres:mySecurePass123@db.xyzproject.supabase.co:5432/postgres
```

### Generic PostgreSQL
```
postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]
```

---

## Quick Commands

### Local Development
```bash
# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium

# Run verification
uv run python verify_setup.py

# Start development server
./run_dev_server.sh
```

### Deployment
```bash
# Push to Hugging Face
git remote add hf https://huggingface.co/spaces/USERNAME/SPACE_NAME
git push hf main

# Or use the deployment workflow
# See .agent/workflows/deploy-to-gcp.md
```

---

## Troubleshooting Quick Fixes

### Database Connection Failed
```bash
# Check connection string format
echo $SUPABASE_DATABASE_URL

# Verify psycopg2 is installed
pip list | grep psycopg2

# Test connection
uv run python -c "from src.database import Database; db = Database(); print(db.use_postgres)"
```

### Missing Dependencies
```bash
# Reinstall all dependencies
uv sync --reinstall

# Or with pip
pip install -r requirements.txt
```

### Playwright Issues
```bash
# Reinstall browsers
uv run playwright install chromium --force

# Check installation
uv run playwright --version
```

---

## File Structure

```
linkedin-scraper-resume/
├── .env                    # Your secrets (DO NOT COMMIT!)
├── .env.example            # Template for environment variables
├── verify_setup.py         # Configuration verification script
├── Dockerfile              # Docker configuration for HF Spaces
├── requirements.txt        # Python dependencies
├── src/
│   ├── database.py         # Database abstraction (SQLite/PostgreSQL)
│   ├── scraper.py          # LinkedIn scraper
│   ├── llm_generator.py    # AI CV generation
│   └── ...
├── docs/
│   ├── SUPABASE_SETUP.md           # Detailed Supabase guide
│   ├── HUGGINGFACE_DEPLOYMENT.md   # Detailed HF deployment guide
│   └── ...
└── data/                   # Local data (gitignored)
```

---

## Security Checklist

- [ ] `.env` file is in `.gitignore`
- [ ] No API keys in code
- [ ] Secrets configured in HF Spaces
- [ ] Database password is strong
- [ ] Connection strings use SSL
- [ ] Regular password rotation

---

## Support & Documentation

- 📖 **Full Setup Guide**: [docs/SUPABASE_SETUP.md](./SUPABASE_SETUP.md)
- 🚀 **Deployment Guide**: [docs/HUGGINGFACE_DEPLOYMENT.md](./HUGGINGFACE_DEPLOYMENT.md)
- 🔧 **Verification Script**: Run `uv run python verify_setup.py`
- 💬 **Issues**: [GitHub Issues](https://github.com/khaldon/linkedin-scrapper-resume/issues)

---

## Common Configuration Scenarios

### Scenario 1: Local Development Only
```bash
# .env file
GOOGLE_API_KEY=your_key_here
DATABASE_PATH=data/jobs.db
HEADLESS=False
```

### Scenario 2: Production on Hugging Face
```bash
# HF Secrets
SUPABASE_DATABASE_URL=postgresql://...
GOOGLE_API_KEY=your_key_here
HEADLESS=True
```

### Scenario 3: Testing with PostgreSQL Locally
```bash
# .env file
SUPABASE_DATABASE_URL=postgresql://...
GOOGLE_API_KEY=your_key_here
HEADLESS=False
```

---

**Last Updated**: 2025-11-21

**Need help?** Run `uv run python verify_setup.py` for automated diagnostics!
