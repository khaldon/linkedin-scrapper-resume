# Contributing to LinkedIn Scraper Resume

Thank you for your interest in contributing! 🎉

## 📋 How to Contribute

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/linkedin-scraper-resume.git
   cd linkedin-scraper-resume
   ```
2. **Create a new branch** for your feature or bug‑fix:
   ```bash
   git checkout -b feature/awesome-feature
   ```
3. **Make your changes** – keep them focused and small.
4. **Run the test scripts** to ensure everything still works:
   ```bash
   uv run python test_gemini_api.py
   ```
5. **Commit with a clear message**:
   ```bash
   git add .
   git commit -m "feat: add awesome feature"
   ```
6. **Push and open a Pull Request**:
   ```bash
   git push origin feature/awesome-feature
   ```
   Then open a PR on GitHub targeting the `main` branch.

## 🛠️ Development Setup

```bash
# Install dependencies (requires uv)
uv sync

# Install Playwright browsers
uv run playwright install chromium

# Copy environment template and fill in your credentials
cp .env.example .env
# Edit .env with your LinkedIn and Gemini API details
```

## ✅ Code Style & Quality

- Follow **PEP 8** conventions.
- Add **type hints** where appropriate.
- Include **docstrings** for public functions/classes.
- Run **ruff** or **flake8** locally before committing.

## 🐛 Reporting Bugs

- Open an issue with a clear title.
- Include steps to reproduce, expected vs actual behavior, and any error logs.
- Attach screenshots or logs if helpful.

## 📚 Documentation

- Keep the `README.md` up‑to‑date.
- Add or update any relevant docs in the `docs/` folder (if created).

## 🤝 Code of Conduct

All contributors must follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## 🎉 Thank You!

Your contributions help make job searching easier for everyone. Happy coding! 🚀
