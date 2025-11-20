# 🚀 Production Deployment Guide - GCP

## Overview

This guide will help you deploy the LinkedIn Job Scraper as a production-ready web application on Google Cloud Platform (GCP). The application will be accessible to anyone on the internet with a beautiful, modern interface.

## Architecture

```
Internet Users
    ↓ (HTTPS)
Google Cloud Load Balancer
    ↓
Cloud Run (Auto-scaling containers)
    ├── FastAPI Backend
    ├── Modern Web Frontend
    └── Playwright Browser Automation
    ↓
Cloud Storage (CVs, Charts, Reports)
    ↓
Cloud SQL PostgreSQL (Job Data)
    ↓
Secret Manager (API Keys, Credentials)
```

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed on your machine
3. **Docker** installed (optional, for local testing)
4. **Domain name** (optional, for custom domain)

## Step-by-Step Deployment

### 1. Initial GCP Setup

```bash
# Install Google Cloud SDK (if not installed)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create linkedin-scraper-prod --name="LinkedIn Scraper"

# Set the project
gcloud config set project linkedin-scraper-prod

# Enable billing (required for Cloud Run)
# Go to: https://console.cloud.google.com/billing
```

### 2. Enable Required APIs

```bash
# Enable all necessary GCP services
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 3. Store Secrets

```bash
# LinkedIn credentials
echo -n "your-linkedin-email@example.com" | \
    gcloud secrets create linkedin-email --data-file=-

echo -n "your-linkedin-password" | \
    gcloud secrets create linkedin-password --data-file=-

# Gemini API key (get from https://makersuite.google.com/app/apikey)
echo -n "your-gemini-api-key" | \
    gcloud secrets create gemini-api-key --data-file=-

# Grant Cloud Run access to secrets
PROJECT_NUMBER=$(gcloud projects describe linkedin-scraper-prod --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding linkedin-email \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding linkedin-password \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding gemini-api-key \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

### 4. Create Cloud Storage Bucket

```bash
# Create bucket for storing generated files
gcloud storage buckets create gs://linkedin-scraper-prod-files \
    --location=us-central1 \
    --uniform-bucket-level-access

# Make bucket publicly readable (for serving charts/CVs)
gcloud storage buckets add-iam-policy-binding gs://linkedin-scraper-prod-files \
    --member=allUsers \
    --role=roles/storage.objectViewer
```

### 5. Build and Deploy

```bash
# Navigate to project directory
cd /home/mohamed/projects/playwright-scraper

# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Or deploy directly with gcloud
gcloud run deploy linkedin-scraper \
    --source . \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --min-instances 0 \
    --max-instances 10 \
    --set-secrets="LINKEDIN_EMAIL=linkedin-email:latest,LINKEDIN_PASSWORD=linkedin-password:latest,GEMINI_API_KEY=gemini-api-key:latest"
```

### 6. Get Your Application URL

```bash
# Get the service URL
gcloud run services describe linkedin-scraper \
    --region us-central1 \
    --format="value(status.url)"

# Output will be something like:
# https://linkedin-scraper-abc123-uc.a.run.app
```

### 7. (Optional) Set Up Custom Domain

```bash
# Map your custom domain
gcloud run domain-mappings create \
    --service linkedin-scraper \
    --domain your-domain.com \
    --region us-central1

# Follow the instructions to add DNS records to your domain provider
```

## Testing the Deployment

### 1. Test the Health Endpoint

```bash
curl https://YOUR-SERVICE-URL/api/health
```

### 2. Open in Browser

Visit your Cloud Run URL in a browser. You should see the beautiful modern interface!

### 3. Test Job Scraping

1. Go to the "Scrape Job" tab
2. Enter a LinkedIn job URL
3. Click "Scrape Job"
4. Wait for the results

## Monitoring and Logging

### View Logs

```bash
# Stream logs in real-time
gcloud run services logs tail linkedin-scraper --region us-central1

# View logs in Cloud Console
# https://console.cloud.google.com/run/detail/us-central1/linkedin-scraper/logs
```

### Set Up Monitoring

1. Go to Cloud Console: https://console.cloud.google.com/monitoring
2. Create alerts for:
   - High error rates
   - High latency
   - Memory usage
   - Request count

### View Metrics

```bash
# View service metrics
gcloud run services describe linkedin-scraper \
    --region us-central1 \
    --format="value(status.url)"
```

## Cost Optimization

### Estimated Monthly Costs

- **Cloud Run**: $0 (free tier) to $30/month
  - First 2 million requests free
  - Pay only when processing requests
  
- **Cloud Storage**: ~$1-5/month
  - $0.020 per GB/month
  
- **Secret Manager**: Free
  - First 6 secret versions free
  
- **Cloud Build**: Free
  - 120 build-minutes/day free

**Total Estimated Cost**: $5-35/month for moderate usage

### Optimization Tips

1. **Use Minimum Instances Wisely**
   ```bash
   # Set min-instances to 0 for development
   gcloud run services update linkedin-scraper \
       --min-instances 0 \
       --region us-central1
   ```

2. **Enable Request Concurrency**
   ```bash
   # Handle multiple requests per instance
   gcloud run services update linkedin-scraper \
       --concurrency 80 \
       --region us-central1
   ```

3. **Set Appropriate Timeouts**
   - Default: 300 seconds
   - For scraping: 3600 seconds (1 hour)

## Security Best Practices

### 1. Enable HTTPS Only
✅ Automatically enabled by Cloud Run

### 2. Use Secret Manager
✅ All credentials stored in Secret Manager

### 3. Implement Rate Limiting

Add to `api.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/scrape")
@limiter.limit("10/hour")
async def scrape_job(request: Request, ...):
    ...
```

### 4. Enable Cloud Armor (Optional)

```bash
# Protect against DDoS attacks
gcloud compute security-policies create linkedin-scraper-policy \
    --description "Security policy for LinkedIn Scraper"
```

### 5. Set Up IAM Properly

```bash
# Restrict who can deploy
gcloud run services add-iam-policy-binding linkedin-scraper \
    --member="user:your-email@example.com" \
    --role="roles/run.admin" \
    --region us-central1
```

## Scaling Configuration

### Auto-scaling Settings

```bash
# Configure auto-scaling
gcloud run services update linkedin-scraper \
    --min-instances 1 \
    --max-instances 10 \
    --concurrency 80 \
    --cpu-throttling \
    --region us-central1
```

### For High Traffic

```bash
# Increase resources
gcloud run services update linkedin-scraper \
    --memory 4Gi \
    --cpu 4 \
    --min-instances 2 \
    --max-instances 20 \
    --region us-central1
```

## Continuous Deployment

### Set Up GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - uses: google-github-actions/setup-gcloud@v0
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: linkedin-scraper-prod
      
      - name: Build and Deploy
        run: |
          gcloud builds submit --config cloudbuild.yaml
```

## Troubleshooting

### Issue: Container fails to start

**Solution**: Check logs
```bash
gcloud run services logs read linkedin-scraper --region us-central1 --limit 50
```

### Issue: Out of memory

**Solution**: Increase memory
```bash
gcloud run services update linkedin-scraper --memory 4Gi --region us-central1
```

### Issue: Timeout errors

**Solution**: Increase timeout
```bash
gcloud run services update linkedin-scraper --timeout 3600 --region us-central1
```

### Issue: Playwright browser crashes

**Solution**: Ensure sufficient memory (2Gi minimum)

## Backup and Disaster Recovery

### 1. Export Database Regularly

```bash
# Export jobs database
gcloud storage cp data/jobs.db gs://linkedin-scraper-prod-backups/jobs-$(date +%Y%m%d).db
```

### 2. Version Control

- All code in Git
- Tag releases
- Keep deployment history

### 3. Rollback Procedure

```bash
# List revisions
gcloud run revisions list --service linkedin-scraper --region us-central1

# Rollback to previous revision
gcloud run services update-traffic linkedin-scraper \
    --to-revisions REVISION_NAME=100 \
    --region us-central1
```

## Performance Optimization

### 1. Enable CDN (for static files)

```bash
# Use Cloud CDN for faster delivery
gcloud compute backend-buckets create linkedin-scraper-static \
    --gcs-bucket-name=linkedin-scraper-prod-files \
    --enable-cdn
```

### 2. Use Connection Pooling

Already implemented in the application.

### 3. Cache Frequently Accessed Data

Implement Redis cache (optional):
```bash
gcloud redis instances create linkedin-scraper-cache \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_6_x
```

## Maintenance

### Regular Tasks

1. **Weekly**: Check logs for errors
2. **Monthly**: Review costs and optimize
3. **Quarterly**: Update dependencies
4. **Yearly**: Review security settings

### Update Deployment

```bash
# Make code changes
git add .
git commit -m "Update feature"
git push

# Redeploy
gcloud builds submit --config cloudbuild.yaml
```

## Support and Resources

- **Cloud Run Docs**: https://cloud.google.com/run/docs
- **Pricing Calculator**: https://cloud.google.com/products/calculator
- **Status Dashboard**: https://status.cloud.google.com
- **Support**: https://cloud.google.com/support

## Success Checklist

- [ ] GCP project created and billing enabled
- [ ] All APIs enabled
- [ ] Secrets stored in Secret Manager
- [ ] Application deployed to Cloud Run
- [ ] Custom domain configured (optional)
- [ ] Monitoring and alerts set up
- [ ] Backup strategy implemented
- [ ] Security best practices applied
- [ ] Documentation updated
- [ ] Team trained on deployment process

---

**🎉 Congratulations! Your application is now live and accessible to users worldwide!**

**Your Application URL**: Check with `gcloud run services describe linkedin-scraper --region us-central1 --format="value(status.url)"`
