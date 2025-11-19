# Google Gemini API Integration Guide

## Overview
This project now integrates Google's Gemini API to generate tailored CVs based on scraped LinkedIn job descriptions.

## Setup Instructions

### 1. Get Your Google API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 2. Configure Environment Variables

Add your API key to the `.env` file:

```bash
GOOGLE_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies

Dependencies are already installed via `uv`:
- `google-generativeai` - Official Google Gemini SDK

## Usage

### Option 1: Full Pipeline (Recommended)

Run the main scraper which includes CV generation:

```bash
python main.py
```

This will:
1. Scrape a LinkedIn job post
2. Save job data to `data/last_scrape.json`
3. Save to database
4. Offer to generate a tailored CV using Gemini API
5. Convert the CV to PDF

### Option 2: Test Gemini API Only

If you already have scraped job data, test the API integration:

```bash
python test_gemini_api.py
```

This will:
1. Load job data from `data/last_scrape.json`
2. Load your current CV from `cv.md`
3. Generate a tailored CV using Gemini API
4. Save to `data/tailored_cv_test.md`
5. Convert to PDF (optional)

### Option 3: Use Gemini API Programmatically

```python
from src.llm_generator import LLMGenerator
import json

# Load job data
with open("data/last_scrape.json", "r") as f:
    job_data = json.load(f)

# Load current CV
with open("cv.md", "r") as f:
    current_cv = f.read()

# Initialize LLM Generator
llm = LLMGenerator()

# Generate tailored CV
tailored_cv = llm.generate_tailored_cv(
    job_description=job_data['full_description'],
    current_cv=current_cv
)

# Save result
with open("tailored_cv.md", "w") as f:
    f.write(tailored_cv)
```

## Features

### LLM Generator (`src/llm_generator.py`)

The `LLMGenerator` class provides:

- **Automatic API Configuration**: Reads `GOOGLE_API_KEY` from environment
- **Model Selection**: Uses `gemini-1.5-flash` by default (fast and cost-effective)
- **Error Handling**: Falls back to simulated response if API fails
- **Safety Settings**: Configured to allow CV-related content
- **Optimized Parameters**:
  - Temperature: 0.7 (balanced creativity)
  - Max tokens: 8192 (supports long CVs)
  - Top-p: 0.95 (diverse outputs)

### Prompt Engineering

The prompt is carefully crafted to:
- Extract ATS keywords from job description
- Maintain truthfulness (no fabrication)
- Quantify achievements
- Use action-oriented language
- Keep professional tone
- Output clean Markdown format

## File Structure

```
playwright-scraper/
├── data/
│   ├── last_scrape.json          # Latest scraped job data
│   ├── tailored_cv_*.md           # Generated CVs
│   └── tailored_cv_*.pdf          # PDF versions
├── src/
│   ├── llm_generator.py           # Google Gemini integration
│   ├── linkedin_auth.py           # LinkedIn authentication
│   ├── scraper.py                 # Job scraping logic
│   ├── database.py                # Database operations
│   └── pdf_converter.py           # Markdown to PDF
├── cv.md                          # Your current CV
├── main.py                        # Main pipeline
├── test_gemini_api.py             # API test script
└── .env                           # Environment variables
```

## API Costs

Google Gemini API pricing (as of 2024):
- **gemini-1.5-flash**: Free tier available
  - 15 requests per minute
  - 1 million tokens per day
  - Very cost-effective for CV generation

For most use cases, the free tier is sufficient.

## Troubleshooting

### Issue: "GOOGLE_API_KEY not set"
**Solution**: Add your API key to `.env` file

### Issue: "Failed to initialize Google Gemini API"
**Solution**: 
- Check your API key is valid
- Ensure you have internet connection
- Verify the API is enabled in Google Cloud Console

### Issue: "Empty response from API"
**Solution**:
- Check if you've exceeded rate limits
- Verify your API key has proper permissions
- Try again in a few moments

### Issue: Simulated response instead of real CV
**Solution**: 
- Ensure `GOOGLE_API_KEY` is set correctly in `.env`
- Don't use the placeholder value `your_google_api_key_here`

## Advanced Configuration

### Use a Different Model

```python
# Use the more powerful gemini-1.5-pro
llm = LLMGenerator(model_name="gemini-1.5-pro")
```

### Custom API Key

```python
# Pass API key directly (not recommended for production)
llm = LLMGenerator(api_key="your_api_key")
```

### Adjust Generation Parameters

Edit `src/llm_generator.py`:

```python
generation_config={
    "temperature": 0.9,      # More creative (0.0-1.0)
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}
```

## Next Steps

1. ✅ Get your Google API key
2. ✅ Add it to `.env` file
3. ✅ Run `python test_gemini_api.py` to test
4. ✅ Run `python main.py` for the full pipeline
5. 🎯 Apply to jobs with your tailored CV!

## Support

For issues or questions:
- Check the logs in `logs/scraper.log`
- Review the error messages in the console
- Ensure all dependencies are installed: `uv sync`

---

**Happy job hunting! 🚀**
