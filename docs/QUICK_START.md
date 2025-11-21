# Quick Start: Google Gemini API Integration

## 🚀 Get Started in 3 Steps

### Step 1: Get Your API Key
Visit: https://makersuite.google.com/app/apikey

### Step 2: Add to .env File
```bash
GOOGLE_API_KEY=AIzaSy...your_actual_key_here
```

### Step 3: Run the Code
```bash
# Test the integration
uv run python test_gemini_api.py

# Or use the simple example
uv run python simple_example.py

# Or run the full pipeline
uv run python main.py
```

---

## 📝 Code Examples

### Minimal Example (5 lines of code!)

```python
from src.llm_generator import LLMGenerator
import json

# Load job data
job_data = json.load(open("data/last_scrape.json"))
current_cv = open("cv.md").read()

# Generate tailored CV
llm = LLMGenerator()
tailored_cv = llm.generate_tailored_cv(
    job_data['full_description'], 
    current_cv
)

# Save result
open("tailored_cv.md", "w").write(tailored_cv)
```

### With Error Handling

```python
from src.llm_generator import LLMGenerator
import json
import os

try:
    # Check API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Set GOOGLE_API_KEY in .env file")
        exit(1)
    
    # Load data
    with open("data/last_scrape.json") as f:
        job_data = json.load(f)
    
    with open("cv.md") as f:
        current_cv = f.read()
    
    # Generate CV
    llm = LLMGenerator()
    tailored_cv = llm.generate_tailored_cv(
        job_data['full_description'],
        current_cv
    )
    
    # Save
    with open("tailored_cv.md", "w") as f:
        f.write(tailored_cv)
    
    print("✅ Success!")
    
except FileNotFoundError as e:
    print(f"❌ File not found: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## 🔧 Available Scripts

| Script | Purpose | Command |
|--------|---------|---------|
| `main.py` | Full pipeline (scrape + generate CV) | `uv run python main.py` |
| `test_gemini_api.py` | Test API with existing JSON | `uv run python test_gemini_api.py` |
| `simple_example.py` | Minimal example | `uv run python simple_example.py` |

---

## 📁 File Locations

- **Input**: `data/last_scrape.json` (scraped job data)
- **Input**: `cv.md` (your current CV)
- **Output**: `data/tailored_cv_*.md` (generated CVs)
- **Output**: `data/tailored_cv_*.pdf` (PDF versions)

---

## 🎯 What Happens When You Run It

1. ✅ Loads job description from JSON
2. ✅ Loads your current CV
3. ✅ Sends to Google Gemini API
4. ✅ Receives tailored CV (10-30 seconds)
5. ✅ Saves as Markdown
6. ✅ Converts to PDF (optional)

---

## 💡 Tips

- **Free Tier**: 15 requests/minute, 1M tokens/day
- **Model**: Uses `gemini-1.5-flash` (fast & free)
- **Fallback**: If API fails, shows simulated response
- **Logs**: Check `logs/scraper.log` for details

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "API key not valid" | Get new key from Google AI Studio |
| "Simulated response" | Check GOOGLE_API_KEY in .env |
| "Module not found" | Run with `uv run python` |
| "File not found" | Run main.py first to scrape job |

---

## 📚 Full Documentation

See `GEMINI_API_GUIDE.md` for complete documentation.

---

**Ready to generate your tailored CV? 🚀**

1. Add your API key to `.env`
2. Run: `uv run python test_gemini_api.py`
3. Check: `data/tailored_cv_test.md`
