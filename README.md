---
title: Linkedin Scraper Resume
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---

# LinkedIn Scraper Resume 🚀

> A powerful pipeline that scrapes LinkedIn job postings and generates AI‑tailored, ATS‑optimized resumes using Google Gemini

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4)](https://ai.google.dev/)

An intelligent pipeline that scrapes LinkedIn job postings and automatically generates tailored, ATS-optimized CVs using Google's Gemini AI. Perfect for job seekers who want to customize their resume for each application.

## ✨ Features

- 🔍 **LinkedIn Job Scraping** - Extract complete job details from LinkedIn URLs
- 💾 **Smart Storage** - Save to JSON files and SQLite database
- 🤖 **AI-Powered CV Generation** - Google Gemini 2.5 Flash integration
- 📄 **PDF Conversion** - Automatic Markdown to PDF conversion
- 🎯 **ATS Optimization** - Intelligent keyword extraction and optimization
- 🔄 **Batch Processing** - Generate CVs for multiple jobs at once
- 🍪 **Session Management** - Persistent LinkedIn authentication
- 🔒 **Privacy First** - All data stored locally

## 📸 Demo

```
Input: LinkedIn Job URL
  ↓
[Scrape] → Job Data (JSON)
  ↓
[AI Generate] → Tailored CV (Markdown)
  ↓
[Convert] → Professional CV (PDF)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- LinkedIn account
- Google Gemini API key (free tier available)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/linkedin-scraper-resume.git
cd linkedin-scraper-resume

# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium

# Set up environment variables
cp .env.example .env
# Edit .env and add your credentials
```

### Configuration

Create a `.env` file with your credentials:

```bash
# LinkedIn Credentials
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Google Gemini API Key (get from https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=your_api_key_here

# Optional
HEADLESS=False
```

### Usage

#### Full Pipeline (Recommended)

```bash
uv run python main.py
```

This will:
1. Prompt for a LinkedIn job URL
2. Scrape the job details
3. Save to database and JSON
4. Generate a tailored CV using AI
5. Convert to PDF

#### Test API Integration

```bash
uv run python test_gemini_api.py
```

Uses existing scraped data to test CV generation.

#### Batch Processing

```bash
uv run python batch_generate_cvs.py
```

Generate CVs for all jobs in the database.

## 📁 Project Structure

```
linkedin-scraper-resume/
├── src/
│   ├── linkedin_auth.py      # LinkedIn authentication
│   ├── scraper.py             # Job scraping logic
│   ├── database.py            # SQLite database operations
│   ├── llm_generator.py       # Google Gemini API integration
│   └── pdf_converter.py       # Markdown to PDF conversion
├── data/                      # Generated data (gitignored)
│   ├── last_scrape.json       # Latest scraped job
│   ├── jobs.db                # SQLite database
│   └── tailored_cv_*.pdf      # Generated CVs
├── main.py                    # Main pipeline script
├── test_gemini_api.py         # API test script
├── simple_example.py          # Minimal example
├── batch_generate_cvs.py      # Batch processor
├── cv.md                      # Your current CV template
└── .env                       # Environment variables (gitignored)
```

## 🤖 How It Works

### 1. Scraping Phase
- Authenticates with LinkedIn using Playwright
- Extracts job title, description, company, and poster info
- Handles anti-bot measures with smart delays

### 2. Storage Phase
- Saves to `data/last_scrape.json`
- Stores in SQLite database for history tracking
- Maintains session cookies for future runs

### 3. AI Generation Phase
- Loads job description and your current CV
- Sends to Google Gemini API with optimized prompt
- Extracts ATS keywords from job description
- Reframes your experience to match requirements
- Maintains truthfulness while optimizing presentation

### 4. Output Phase
- Saves as clean Markdown
- Converts to professional PDF
- Stores in database with job reference

## 💻 Code Example

```python
from src.llm_generator import LLMGenerator
import json

# Load scraped job data
with open("data/last_scrape.json") as f:
    job = json.load(f)

# Load your CV
with open("cv.md") as f:
    cv = f.read()

# Generate tailored CV
llm = LLMGenerator()
tailored_cv = llm.generate_tailored_cv(
    job['full_description'], 
    cv
)

# Save result
with open("tailored_cv.md", "w") as f:
    f.write(tailored_cv)
```

## 🔧 Advanced Configuration

### Use Different AI Model

```python
# Use the more powerful Gemini Pro
llm = LLMGenerator(model_name="gemini-2.5-pro")
```

### Customize Generation Parameters

Edit `src/llm_generator.py`:

```python
generation_config={
    "temperature": 0.9,      # More creative (0.0-1.0)
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}
```

## 📚 Documentation

- [Quick Start Guide](QUICK_START.md) - Get started in 5 minutes
- [API Guide](GEMINI_API_GUIDE.md) - Complete Gemini API setup
- [Architecture](ARCHITECTURE.md) - System design and flow
- [Contributing](CONTRIBUTING.md) - How to contribute

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not valid" | Get new key from [Google AI Studio](https://makersuite.google.com/app/apikey) |
| "Module not found" | Run with `uv run python` |
| "Login failed" | Check LinkedIn credentials in `.env` |
| "File not found" | Run `main.py` to scrape a job first |

Check `logs/scraper.log` for detailed error messages.

## 💰 API Costs

**Google Gemini API (Free Tier)**
- 15 requests per minute
- 1 million tokens per day
- Free for most use cases

**Estimated Usage**
- 1 CV generation ≈ 3,000-5,000 tokens
- ~200-300 CVs per day (free!)

## 🔒 Privacy & Security

- ✅ All data stored locally
- ✅ No data sent to third parties (except Google Gemini for CV generation)
- ✅ Credentials stored in `.env` (never committed)
- ✅ `.gitignore` configured to protect sensitive data

**Never commit:**
- API keys
- Passwords
- Personal data
- Scraped job data
- Generated CVs

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) for AI-powered CV generation
- [Playwright](https://playwright.dev/) for browser automation
- [WeasyPrint](https://weasyprint.org/) for PDF conversion

## ⚠️ Disclaimer

This tool is for personal use only. Please respect LinkedIn's Terms of Service and use responsibly. The authors are not responsible for any misuse of this tool.

## 📞 Support

- 📖 Check the [documentation](GEMINI_API_GUIDE.md)
- 🐛 [Report bugs](https://github.com/YOUR_USERNAME/linkedin-scraper-resume/issues)
- 💡 [Request features](https://github.com/YOUR_USERNAME/linkedin-scraper-resume/issues)

---

**Made with ❤️ for job seekers**

*Star ⭐ this repo if it helped you land a job!*
