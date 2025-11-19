# LinkedIn Job Scraper + Google Gemini API Integration

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     LINKEDIN JOB SCRAPER                        │
│                     + CV TAILORING SYSTEM                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│  LinkedIn URL   │
│  (Job Posting)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    1. SCRAPING PHASE                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  linkedin_auth.py                                        │  │
│  │  • Authenticate with LinkedIn                            │  │
│  │  • Handle cookies & sessions                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  scraper.py                                              │  │
│  │  • Extract job title, description, company               │  │
│  │  • Extract poster information                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    2. STORAGE PHASE                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  data/last_scrape.json                                   │  │
│  │  {                                                        │  │
│  │    "title": "Machine Learning Engineer",                 │  │
│  │    "company": "BlackStone eIT",                          │  │
│  │    "description": "...",                                 │  │
│  │    "full_description": "...",                            │  │
│  │    "poster": "...",                                      │  │
│  │    "url": "..."                                          │  │
│  │  }                                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  database.py → data/jobs.db (SQLite)                     │  │
│  │  • Save job details                                      │  │
│  │  • Track generated CVs                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    3. AI GENERATION PHASE                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  llm_generator.py                                        │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  Google Gemini API (gemini-1.5-flash)             │  │  │
│  │  │  • Read GOOGLE_API_KEY from .env                  │  │  │
│  │  │  • Configure model parameters                     │  │  │
│  │  │  • Set safety settings                            │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  │                                                          │  │
│  │  Input:                                                  │  │
│  │  ├─ Job Description (from JSON)                         │  │
│  │  └─ Current CV (cv.md)                                  │  │
│  │                                                          │  │
│  │  Prompt Engineering:                                     │  │
│  │  ├─ Extract ATS keywords                                │  │
│  │  ├─ Match skills to job requirements                    │  │
│  │  ├─ Reframe experiences                                 │  │
│  │  ├─ Quantify achievements                               │  │
│  │  └─ Maintain truthfulness                               │  │
│  │                                                          │  │
│  │  Output:                                                 │  │
│  │  └─ Tailored CV (Markdown)                              │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    4. OUTPUT PHASE                              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  data/tailored_cv_X.md                                   │  │
│  │  • Markdown format                                       │  │
│  │  • ATS optimized                                         │  │
│  │  • Job-specific keywords                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  pdf_converter.py → data/tailored_cv_X.pdf              │  │
│  │  • Convert Markdown to PDF                               │  │
│  │  • Professional formatting                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
LinkedIn URL
    ↓
[Scraper] → Job Data (JSON)
    ↓
[Database] → SQLite Storage
    ↓
[LLM Generator] → Google Gemini API
    ↓           ↖ Current CV (cv.md)
Tailored CV (Markdown)
    ↓
[PDF Converter] → Tailored CV (PDF)
```

## Key Components

### 1. **linkedin_auth.py**
- Handles LinkedIn authentication
- Manages browser sessions
- Stores/loads cookies

### 2. **scraper.py**
- Extracts job information
- Parses HTML content
- Returns structured data

### 3. **database.py**
- SQLite database operations
- Stores jobs and generated CVs
- Tracks generation history

### 4. **llm_generator.py** ⭐ NEW
- Google Gemini API integration
- Prompt engineering
- Error handling & fallback
- Configuration:
  - Model: gemini-1.5-flash
  - Temperature: 0.7
  - Max tokens: 8192

### 5. **pdf_converter.py**
- Markdown to PDF conversion
- Professional formatting
- Uses WeasyPrint

## Environment Variables

```bash
# LinkedIn Credentials
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Google Gemini API
GOOGLE_API_KEY=AIzaSy...your_key_here

# Optional
HEADLESS=False
```

## Usage Patterns

### Pattern 1: Full Pipeline
```bash
uv run python main.py
# Scrape → Store → Generate CV → Convert to PDF
```

### Pattern 2: Test API Only
```bash
uv run python test_gemini_api.py
# Use existing JSON → Generate CV
```

### Pattern 3: Batch Processing
```bash
uv run python batch_generate_cvs.py
# Process all jobs in database
```

### Pattern 4: Custom Script
```python
from src.llm_generator import LLMGenerator
import json

job = json.load(open("data/last_scrape.json"))
cv = open("cv.md").read()

llm = LLMGenerator()
result = llm.generate_tailored_cv(job['full_description'], cv)

open("output.md", "w").write(result)
```

## API Request Flow

```
Python Code
    ↓
llm_generator.py
    ↓
google.generativeai SDK
    ↓
HTTPS Request → Google Gemini API
    ↓
AI Processing (10-30 seconds)
    ↓
Response (Tailored CV)
    ↓
Save to file
```

## Error Handling

```
Try:
    Initialize Gemini API
    ↓
    Send request
    ↓
    Receive response
    ↓
    Return tailored CV

Catch:
    API Key Invalid → Log error + Simulated response
    Network Error → Log error + Simulated response
    Rate Limit → Log error + Simulated response
    Other Error → Log error + Simulated response
```

## File Structure

```
playwright-scraper/
├── src/
│   ├── linkedin_auth.py      # LinkedIn authentication
│   ├── scraper.py             # Job scraping logic
│   ├── database.py            # Database operations
│   ├── llm_generator.py       # ⭐ Google Gemini integration
│   └── pdf_converter.py       # PDF conversion
├── data/
│   ├── last_scrape.json       # Latest scraped job
│   ├── jobs.db                # SQLite database
│   ├── tailored_cv_*.md       # Generated CVs
│   └── tailored_cv_*.pdf      # PDF versions
├── main.py                    # Full pipeline
├── test_gemini_api.py         # API test script
├── simple_example.py          # Minimal example
├── batch_generate_cvs.py      # Batch processor
├── cv.md                      # Your current CV
├── .env                       # Environment variables
└── GEMINI_API_GUIDE.md        # Full documentation
```

## Next Steps

1. ✅ Get Google API key
2. ✅ Add to .env file
3. ✅ Run test script
4. ✅ Generate tailored CVs
5. 🎯 Apply to jobs!
