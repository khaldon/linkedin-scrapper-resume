# 🔧 Quick Setup Guide

## Step 1: Configure Environment Variables

The application needs your LinkedIn credentials and Gemini API key to work. Follow these steps:

### 1. Copy the example file

```bash
cp .env.example .env
```

### 2. Edit the .env file

Open `.env` in your text editor and add your credentials:

```bash
# LinkedIn Credentials
LINKEDIN_EMAIL=your_actual_email@example.com
LINKEDIN_PASSWORD=your_actual_password

# Google Gemini API Key
GOOGLE_API_KEY=your_actual_gemini_api_key
```

### 3. Get Your Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key and paste it in your `.env` file

### 4. Restart the Server

If the server is already running, stop it (Ctrl+C) and restart:

```bash
./run_dev_server.sh
```

---

## Step 2: Test the Application

1. **Open your browser**: http://localhost:8080

2. **Try scraping a job**:
   - Go to LinkedIn and find a job posting
   - Copy the URL (e.g., `https://www.linkedin.com/jobs/view/1234567890`)
   - Paste it in the "Scrape Job" tab
   - Click "Scrape Job"

3. **Generate a CV**:
   - Go to "Generate CV" tab
   - Select a scraped job
   - Upload your CV (`.md` or `.txt` file)
   - Click "Generate Tailored CV"

4. **View Statistics**:
   - Go to "Market Stats" tab
   - Click "Generate Fresh Stats"
   - View the colorful charts and recommendations

---

## Troubleshooting

### Error: "LinkedIn credentials not configured"

**Solution**: Make sure you've created a `.env` file with your credentials.

```bash
# Check if .env exists
ls -la .env

# If not, copy from example
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

### Error: "Module not found"

**Solution**: Install dependencies

```bash
uv sync
```

### Error: "Playwright browser not found"

**Solution**: Install Playwright browsers

```bash
playwright install chromium
```

### Server won't start

**Solution**: Check if port 8080 is already in use

```bash
# Check what's using port 8080
lsof -i :8080

# Kill the process if needed
kill -9 <PID>

# Or use a different port
uvicorn api:app --host 0.0.0.0 --port 8081
```

---

## Security Notes

⚠️ **IMPORTANT**: Never commit your `.env` file to Git!

The `.env` file is already in `.gitignore`, so it won't be committed. But double-check:

```bash
# Verify .env is ignored
git status

# .env should NOT appear in the list
```

---

## Next Steps

Once everything is working locally:

1. **Test all features** to make sure they work
2. **Review the code** to understand how it works
3. **Deploy to GCP** when ready (see `PRODUCTION_DEPLOYMENT.md`)

---

## Quick Reference

**Start server**: `./run_dev_server.sh`
**Stop server**: Press `Ctrl+C`
**View logs**: Check the terminal output
**API docs**: http://localhost:8080/docs
**Frontend**: http://localhost:8080

---

**Need more help?** Check the full documentation:
- `PRODUCTION_DEPLOYMENT.md` - Deployment guide
- `PRODUCTION_READY_SUMMARY.md` - Feature overview
- `README.md` - Project overview
