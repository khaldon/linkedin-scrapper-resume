# LinkedIn Job Scraper + AI CV Generator 🚀

An automated pipeline that scrapes LinkedIn job postings and generates tailored, ATS-optimized CVs using Google's Gemini AI.

![Workflow](/.gemini/antigravity/brain/2d1d25be-3674-4cdb-b4d0-7c3295ffad33/workflow_diagram_1763591795056.png)

## ✨ Features

- 🔍 **LinkedIn Job Scraping** - Extract job details from LinkedIn URLs
- 💾 **Data Storage** - Save to JSON files and SQLite database
- 🤖 **AI-Powered CV Generation** - Google Gemini API integration
- 📄 **PDF Conversion** - Automatic Markdown to PDF conversion
- 🎯 **ATS Optimization** - Keyword extraction and optimization
- 🔄 **Batch Processing** - Generate CVs for multiple jobs
- 🍪 **Session Management** - Persistent LinkedIn authentication

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
cd /home/mohamed/projects/playwright-scraper

# Install dependencies (already done)
uv sync

# Install Playwright browsers
uv run playwright install chromium
```

### 2. Configuration

Create/update `.env` file:

```bash
# LinkedIn Credentials
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Google Gemini API Key (get from https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=your_api_key_here

# Optional
HEADLESS=False
```

### 3. Usage

#### Option A: Full Pipeline (Recommended)

```bash
uv run python main.py
```

This will:
1. Prompt for a LinkedIn job URL
2. Scrape the job details
3. Save to database and JSON
4. Offer to generate a tailored CV
5. Convert to PDF

#### Option B: Test API Integration

```bash
uv run python test_gemini_api.py
```

Uses existing scraped data to test CV generation.

#### Option C: Simple Example

```bash
uv run python simple_example.py
```

Minimal code example for quick testing.

#### Option D: Batch Processing

```bash
uv run python batch_generate_cvs.py
```

Generate CVs for all jobs in the database.

## 📁 Project Structure

```
playwright-scraper/
├── src/
│   ├── linkedin_auth.py      # LinkedIn authentication
│   ├── scraper.py             # Job scraping logic
│   ├── database.py            # SQLite database operations
│   ├── llm_generator.py       # Google Gemini API integration ⭐
│   └── pdf_converter.py       # Markdown to PDF conversion
├── data/
│   ├── last_scrape.json       # Latest scraped job
│   ├── jobs.db                # SQLite database
│   ├── tailored_cv_*.md       # Generated CVs (Markdown)
│   └── tailored_cv_*.pdf      # Generated CVs (PDF)
├── main.py                    # Main pipeline script
├── test_gemini_api.py         # API test script
├── simple_example.py          # Minimal example
├── batch_generate_cvs.py      # Batch processor
├── cv.md                      # Your current CV
└── .env                       # Environment variables
```

## 🤖 Google Gemini API Integration

### Setup

1. **Get API Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Add to .env**: `GOOGLE_API_KEY=your_key_here`
3. **Test**: Run `uv run python test_gemini_api.py`

### Features

- ✅ Automatic API configuration
- ✅ Error handling with fallback
- ✅ ATS keyword optimization
- ✅ Professional prompt engineering
- ✅ Free tier: 15 req/min, 1M tokens/day

### Code Example

```python
from src.llm_generator import LLMGenerator
import json

# Load job data
job = json.load(open("data/last_scrape.json"))
cv = open("cv.md").read()

# Generate tailored CV
llm = LLMGenerator()
tailored_cv = llm.generate_tailored_cv(
    job['full_description'], 
    cv
)

# Save result
open("tailored_cv.md", "w").write(tailored_cv)
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [QUICK_START.md](QUICK_START.md) | Quick reference guide |
| [GEMINI_API_GUIDE.md](GEMINI_API_GUIDE.md) | Complete API setup guide |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture |
| [SUMMARY.md](SUMMARY.md) | Integration summary |

## 🎯 How It Works

### 1. Scraping Phase
- Authenticate with LinkedIn
- Extract job title, description, company
- Extract poster information
- Handle anti-bot measures

### 2. Storage Phase
- Save to `data/last_scrape.json`
- Store in SQLite database
- Track generation history

### 3. AI Generation Phase
- Load job description and current CV
- Send to Google Gemini API
- Extract ATS keywords
- Reframe experiences
- Optimize for job requirements

### 4. Output Phase
- Save as Markdown
- Convert to PDF
- Store in database

## 🔧 Technical Details

### Technologies Used

- **Python 3.12+**
- **Playwright** - Browser automation
- **Google Generative AI** - Gemini API
- **SQLite** - Database
- **WeasyPrint** - PDF generation
- **python-dotenv** - Environment management

### API Configuration

```python
Model: gemini-1.5-flash
Temperature: 0.7
Max Tokens: 8192
Top-p: 0.95
Top-k: 40
```

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| "API key not valid" | Get new key from Google AI Studio |
| "Module not found" | Run with `uv run python` |
| "Simulated response" | Check GOOGLE_API_KEY in .env |
| "File not found" | Run main.py to scrape job first |
| "Login failed" | Check LinkedIn credentials |

### Logs

Check `logs/scraper.log` for detailed error messages.

## 💰 API Costs

**Google Gemini API (Free Tier)**
- 15 requests per minute
- 1 million tokens per day
- Free for most use cases

**Estimated Usage**
- 1 CV generation ≈ 3,000-5,000 tokens
- ~200-300 CVs per day (free!)

## 🎓 Example Workflow

```bash
# 1. Scrape a job
uv run python main.py
# Enter: https://www.linkedin.com/jobs/view/123456789

# 2. Generate tailored CV
# (Follow prompts in main.py)

# 3. Check output
ls data/tailored_cv_*.pdf

# 4. Apply to job with tailored CV! 🎉
```

## 📊 Sample Output

### Input (Job Description)
```
Machine Learning Engineer
- 2-3 years experience
- Python, TensorFlow, PyTorch
- ML algorithms and tools
- REST APIs
```

### Output (Tailored CV)
```markdown
# Mohamed Khaled
## Machine Learning Engineer | Python & ML Specialist

### Professional Summary
Machine Learning Engineer with 1+ years specializing in 
NLP and LLMs. Proficient in Python, TensorFlow, and PyTorch.
Experienced in deploying ML models via REST APIs...

### Technical Skills
- **ML Frameworks**: TensorFlow, PyTorch, Scikit-Learn
- **Programming**: Python (Advanced), SQL
- **Deployment**: FastAPI, Flask, Docker, REST APIs
...
```

## 🤝 Contributing

This is a personal project, but feel free to fork and adapt!

## 📝 License

MIT License - Feel free to use for your job search!

## 🙏 Acknowledgments

- Google Gemini API for AI generation
- Playwright for browser automation
- WeasyPrint for PDF conversion

## 📞 Support

For issues:
1. Check the logs: `logs/scraper.log`
2. Review documentation in `GEMINI_API_GUIDE.md`
3. Verify environment variables in `.env`

---

**Made with ❤️ for job seekers**

*Last updated: 2025-11-20*
