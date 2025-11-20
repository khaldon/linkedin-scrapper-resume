---
description: Deploy LinkedIn Job Scraper to GCP for Production
---

# Deploy to Google Cloud Platform (GCP)

This workflow guides you through deploying the LinkedIn Job Scraper as a production web application on GCP.

## Architecture Overview

```
User Browser
    ↓
Cloud Load Balancer (HTTPS)
    ↓
Cloud Run (Frontend + API)
    ↓
Cloud SQL (PostgreSQL) - Job Data
    ↓
Cloud Storage - Generated CVs, Charts
    ↓
Secret Manager - API Keys, Credentials
```

## Prerequisites

1. **GCP Account Setup**
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize gcloud
gcloud init

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

2. **Enable Required APIs**
```bash
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable storage-api.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

## Step 1: Prepare the Application

// turbo
1. Build the production frontend and API
```bash
cd /home/mohamed/projects/playwright-scraper
```

## Step 2: Set Up Cloud SQL (PostgreSQL)

2. Create a PostgreSQL instance
```bash
gcloud sql instances create linkedin-scraper-db \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=us-central1 \
    --root-password=YOUR_SECURE_PASSWORD
```

3. Create the database
```bash
gcloud sql databases create jobs_db \
    --instance=linkedin-scraper-db
```

## Step 3: Set Up Cloud Storage

4. Create storage bucket for files
```bash
gcloud storage buckets create gs://YOUR_PROJECT_ID-linkedin-scraper \
    --location=us-central1 \
    --uniform-bucket-level-access
```

## Step 4: Store Secrets

5. Store sensitive credentials
```bash
# LinkedIn credentials
echo -n "your-linkedin-email@example.com" | \
    gcloud secrets create linkedin-email --data-file=-

echo -n "your-linkedin-password" | \
    gcloud secrets create linkedin-password --data-file=-

# Gemini API key
echo -n "your-gemini-api-key" | \
    gcloud secrets create gemini-api-key --data-file=-

# Database password
echo -n "YOUR_SECURE_PASSWORD" | \
    gcloud secrets create db-password --data-file=-
```

## Step 5: Build and Deploy to Cloud Run

6. Build the container
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/linkedin-scraper
```

7. Deploy to Cloud Run
```bash
gcloud run deploy linkedin-scraper \
    --image gcr.io/YOUR_PROJECT_ID/linkedin-scraper \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --set-env-vars="DATABASE_URL=postgresql://postgres:PASSWORD@/jobs_db?host=/cloudsql/YOUR_PROJECT_ID:us-central1:linkedin-scraper-db" \
    --set-secrets="LINKEDIN_EMAIL=linkedin-email:latest,LINKEDIN_PASSWORD=linkedin-password:latest,GEMINI_API_KEY=gemini-api-key:latest" \
    --add-cloudsql-instances YOUR_PROJECT_ID:us-central1:linkedin-scraper-db
```

## Step 6: Set Up Custom Domain (Optional)

8. Map custom domain
```bash
gcloud run domain-mappings create \
    --service linkedin-scraper \
    --domain your-domain.com \
    --region us-central1
```

## Step 7: Configure Monitoring

9. Set up logging and monitoring
```bash
# Logs are automatically sent to Cloud Logging
# View logs:
gcloud run services logs read linkedin-scraper --region us-central1

# Set up alerts in Cloud Monitoring console
```

## Cost Optimization

- **Cloud Run**: Pay only when requests are being processed
- **Cloud SQL**: Use db-f1-micro for development (can upgrade later)
- **Cloud Storage**: Pay for storage used
- **Estimated monthly cost**: $10-30 for low traffic

## Security Checklist

- [ ] All secrets stored in Secret Manager
- [ ] Cloud SQL uses private IP
- [ ] HTTPS enforced via Cloud Run
- [ ] IAM roles properly configured
- [ ] Regular backups enabled for Cloud SQL
- [ ] Rate limiting implemented in application

## Scaling Configuration

For high traffic, update Cloud Run settings:
```bash
gcloud run services update linkedin-scraper \
    --min-instances 1 \
    --max-instances 10 \
    --concurrency 80 \
    --region us-central1
```

## Rollback

If deployment fails:
```bash
gcloud run services update-traffic linkedin-scraper \
    --to-revisions PREVIOUS_REVISION=100 \
    --region us-central1
```

## Monitoring URLs

- **Application**: https://linkedin-scraper-HASH-uc.a.run.app
- **Cloud Console**: https://console.cloud.google.com
- **Logs**: https://console.cloud.google.com/logs
- **Metrics**: https://console.cloud.google.com/monitoring
