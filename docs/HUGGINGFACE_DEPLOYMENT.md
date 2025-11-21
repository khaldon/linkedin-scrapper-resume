# 🤗 Hugging Face Spaces Deployment Guide

Complete guide for deploying LinkedIn Scraper Resume to Hugging Face Spaces with Supabase PostgreSQL.

## Why Hugging Face Spaces?

- ✅ **Free Hosting**: Free tier for public spaces
- ✅ **Docker Support**: Full control with Docker SDK
- ✅ **Easy Deployment**: Git push to deploy
- ✅ **Auto-scaling**: Handles traffic automatically
- ✅ **Built-in Secrets**: Secure environment variable management

## Prerequisites

Before deploying, ensure you have:

1. ✅ A Hugging Face account ([sign up here](https://huggingface.co/join))
2. ✅ A Supabase project with PostgreSQL database ([setup guide](./SUPABASE_SETUP.md))
3. ✅ Google Gemini API key ([get one here](https://makersuite.google.com/app/apikey))
4. ✅ Git installed and configured

## Step-by-Step Deployment

### 1. Create a Hugging Face Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Fill in the details:
   - **Owner**: Your username or organization
   - **Space name**: `linkedin-scraper-resume` (or your choice)
   - **License**: MIT
   - **Select the Space SDK**: **Docker**
   - **Space hardware**: CPU basic (free tier)
   - **Visibility**: Public or Private

3. Click **Create Space**

### 2. Configure Repository Secrets

**IMPORTANT**: Never commit sensitive data to Git. Use Hugging Face Secrets instead.

1. In your Space, click **Settings**
2. Scroll to **Repository secrets**
3. Add these secrets:

| Secret Name | Value | Required |
|-------------|-------|----------|
| `SUPABASE_DATABASE_URL` | Your Supabase connection string | ✅ Yes |
| `GOOGLE_API_KEY` | Your Google Gemini API key | ✅ Yes |
| `HEADLESS` | `True` | Optional |

**Example values**:
```
SUPABASE_DATABASE_URL=postgresql://postgres:mypass@db.xyz.supabase.co:5432/postgres
GOOGLE_API_KEY=AIzaSyD...your_key_here
HEADLESS=True
```

### 3. Push Your Code to Hugging Face

#### Option A: Direct Push (Recommended)

```bash
# Navigate to your project
cd /home/mohamed/projects/playwright-scraper

# Add Hugging Face remote
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/linkedin-scraper-resume

# Push to Hugging Face
git push hf main
```

#### Option B: Clone and Push

```bash
# Clone the HF Space repository
git clone https://huggingface.co/spaces/YOUR_USERNAME/linkedin-scraper-resume
cd linkedin-scraper-resume

# Copy your project files
cp -r /home/mohamed/projects/playwright-scraper/* .

# Commit and push
git add .
git commit -m "Initial deployment"
git push
```

### 4. Monitor Deployment

1. Go to your Space page
2. Click on **Logs** tab
3. Watch the build process:
   - Installing dependencies
   - Installing Playwright browsers
   - Starting the application

4. Wait for the status to show **Running** (usually 3-5 minutes)

### 5. Verify Deployment

Once deployed, you should see:

```
✅ Application running on https://huggingface.co/spaces/YOUR_USERNAME/linkedin-scraper-resume
```

Test the application:
1. Open the Space URL
2. Try scraping a LinkedIn job URL
3. Generate a CV
4. Check database persistence by refreshing the page

## Configuration Files

### Required Files for HF Deployment

Ensure these files are in your repository:

#### `README.md` (with HF metadata)

The top of your README.md should have:

```yaml
---
title: Linkedin Scraper Resume
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
app_port: 7860
---
```

#### `Dockerfile`

Your Dockerfile should:
- Use Python 3.12
- Install system dependencies for Playwright
- Install Python packages
- Install Playwright browsers
- Expose port 7860
- Run as non-root user

See the existing `Dockerfile` in the project.

#### `.gitignore`

Ensure sensitive files are ignored:
```
.env
data/
logs/
*.db
__pycache__/
```

## Environment Variables

The application automatically detects the environment:

### On Hugging Face Spaces

```python
# Automatically set by HF
SPACE_ID=your_username/linkedin-scraper-resume
PORT=7860

# Set by you in Secrets
SUPABASE_DATABASE_URL=postgresql://...
GOOGLE_API_KEY=AIza...
```

### Database Selection Logic

```python
# In src/database.py
db_url = os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")
use_postgres = bool(db_url and HAS_POSTGRES)

if use_postgres:
    # Use Supabase PostgreSQL
else:
    # Fall back to SQLite (ephemeral on HF!)
```

## Troubleshooting

### Build Fails

**Error**: `Failed to build`

**Solutions**:
1. Check Dockerfile syntax
2. Verify all dependencies in `requirements.txt`
3. Check build logs for specific errors
4. Ensure Python version is 3.12

### Application Crashes on Startup

**Error**: `Application error`

**Solutions**:
1. Check logs for error messages
2. Verify secrets are set correctly
3. Test database connection
4. Ensure port 7860 is exposed

### Database Connection Failed

**Error**: `connection to server failed`

**Solutions**:
1. Verify `SUPABASE_DATABASE_URL` secret is set
2. Check Supabase project is active
3. Verify connection string format
4. Test connection locally first

### Playwright Browser Not Found

**Error**: `Executable doesn't exist`

**Solutions**:
1. Ensure `playwright install chromium` runs in Dockerfile
2. Check it runs as the correct user (appuser)
3. Verify system dependencies are installed

### Port Issues

**Error**: `Port 7860 not accessible`

**Solutions**:
1. Ensure `EXPOSE 7860` in Dockerfile
2. Check `app_port: 7860` in README.md metadata
3. Verify uvicorn binds to `0.0.0.0:7860`

## Performance Optimization

### 1. Use Persistent Storage (Supabase)

✅ **DO**: Use Supabase for all data
❌ **DON'T**: Rely on local file storage (it's ephemeral!)

### 2. Optimize Docker Image

```dockerfile
# Use slim images
FROM python:3.12-slim

# Multi-stage builds for smaller images
# Cache dependencies
RUN pip install --no-cache-dir -r requirements.txt
```

### 3. Configure Workers

For CPU basic (free tier):
```python
# In Dockerfile CMD
CMD exec uvicorn api:app --host 0.0.0.0 --port ${PORT} --workers 1
```

For upgraded hardware:
```python
--workers 2  # or more
```

## Monitoring and Maintenance

### Check Application Health

1. **Logs**: Monitor in HF Space → Logs tab
2. **Metrics**: Check CPU/Memory usage
3. **Database**: Monitor in Supabase dashboard

### Update Deployment

```bash
# Make changes locally
git add .
git commit -m "Update: description"

# Push to HF (triggers rebuild)
git push hf main
```

### Rollback

```bash
# View commit history
git log

# Rollback to previous commit
git reset --hard COMMIT_HASH
git push hf main --force
```

## Cost Considerations

### Free Tier Limits

**Hugging Face Spaces (Free)**:
- CPU basic (2 vCPU, 16 GB RAM)
- Always-on (may sleep after inactivity)
- Public spaces only

**Supabase (Free)**:
- 500 MB database
- 5 GB bandwidth
- Unlimited API requests

### Upgrade Options

If you need more resources:

**Hugging Face**:
- CPU upgrade: $0.03/hour
- GPU: Starting at $0.60/hour

**Supabase**:
- Pro: $25/month (8 GB database, 50 GB bandwidth)

## Security Best Practices

### 1. Never Commit Secrets

```bash
# Always use .gitignore
.env
*.key
secrets/
```

### 2. Use HF Secrets

✅ Store all sensitive data in HF Repository Secrets
❌ Never hardcode API keys or passwords

### 3. Validate Input

```python
# In your API endpoints
from pydantic import HttpUrl

class ScrapeRequest(BaseModel):
    url: HttpUrl  # Validates URL format
```

### 4. Rate Limiting

Consider adding rate limiting for public deployments:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/scrape")
@limiter.limit("10/minute")
async def scrape_job(request: Request):
    # Your code here
```

## Testing Before Deployment

### Local Testing

```bash
# Run verification
uv run python verify_setup.py

# Test with Docker locally
docker build -t linkedin-scraper .
docker run -p 7860:7860 \
  -e SUPABASE_DATABASE_URL="your_url" \
  -e GOOGLE_API_KEY="your_key" \
  linkedin-scraper
```

### Staging Environment

Consider creating a separate HF Space for testing:
- `linkedin-scraper-resume-staging`
- Test all features before pushing to production

## Useful Commands

### View Logs

```bash
# In HF Space, click "Logs" tab
# Or use HF CLI
huggingface-cli space logs YOUR_USERNAME/linkedin-scraper-resume
```

### Restart Space

1. Go to Space Settings
2. Click "Factory reboot"
3. Wait for rebuild

### Delete Space

1. Go to Space Settings
2. Scroll to "Danger Zone"
3. Click "Delete this Space"

## Next Steps

After successful deployment:

1. ✅ Test all features thoroughly
2. ✅ Monitor logs for errors
3. ✅ Set up database backups
4. ✅ Share your Space with users!
5. ✅ Consider adding analytics

## Support Resources

- 📚 [HF Spaces Documentation](https://huggingface.co/docs/hub/spaces)
- 💬 [HF Discord](https://discord.gg/hugging-face)
- 🐛 [Report Issues](https://github.com/huggingface/hub-docs/issues)
- 📖 [Docker SDK Guide](https://huggingface.co/docs/hub/spaces-sdks-docker)

---

**Ready to deploy?** Follow the steps above and your app will be live in minutes! 🚀

**Questions?** Check the [troubleshooting section](#troubleshooting) or open an issue.
