# Release v1.0.0 – Initial Release

## Overview

- **Project:** linkedin-scraper-resume
- **Version:** 1.0.0
- **Date:** 2025-11-20
- **Description:** Automated LinkedIn job scraper with AI‑powered CV tailoring using Google Gemini. Includes full pipeline for scraping, storing, generating ATS‑optimized CVs, and PDF conversion.

## Features

- LinkedIn authentication & job scraping via Playwright
- SQLite storage of scraped jobs
- Google Gemini 2.5‑Flash integration for CV generation
- Markdown → PDF conversion with WeasyPrint
- Batch processing for multiple jobs
- Comprehensive documentation, CI‑ready scripts, and contribution guidelines

## Getting Started

```bash
# Clone the repo
git clone https://github.com/khaldon/linkedin-scrapper-resume.git
cd linkedin-scrapper-resume

# Install dependencies (uv required)
uv sync
uv run playwright install chromium

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials and Gemini API key
```

Run the main pipeline:
```bash
uv run python main.py
```

## Release Assets

- Source code (tagged as `v1.0.0`)
- `LICENSE` – MIT License
- Documentation files (`README.md`, `GEMINI_API_GUIDE.md`, etc.)

## Acknowledgements

- Google Gemini for the LLM API
- Playwright for browser automation
- WeasyPrint for PDF generation

---

*This release is licensed under the MIT License.*
