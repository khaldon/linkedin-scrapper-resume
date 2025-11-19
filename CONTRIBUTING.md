# Contributing to LinkedIn Job Scraper + AI CV Generator

Thank you for your interest in contributing! This project helps job seekers create tailored CVs using AI.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/playwright-scraper.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test thoroughly
6. Submit a pull request

## 🔧 Development Setup

```bash
# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium

# Copy environment template
cp .env.example .env

# Add your credentials to .env
```

## 📝 Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small
- Write descriptive commit messages

## 🧪 Testing

Before submitting a PR:

```bash
# Test the scraper
uv run python main.py

# Test the API integration
uv run python test_gemini_api.py
```

## 🐛 Reporting Bugs

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages and logs

## 💡 Feature Requests

We welcome feature requests! Please:

- Check if it's already been requested
- Explain the use case
- Describe the expected behavior

## 🔒 Security

**NEVER commit:**
- API keys
- Passwords
- Personal data
- Scraped job data
- Generated CVs

Always use `.env` for sensitive data.

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Every contribution helps make job searching easier for everyone!
