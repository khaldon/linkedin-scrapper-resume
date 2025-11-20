# Production Deployment Guide

This guide explains how to deploy the `linkedin-scraper-resume` application to **Google Cloud Run**.

## Prerequisites

1.  **Google Cloud Project**: You need a GCP project with billing enabled.
2.  **gcloud CLI**: Installed and authenticated (`gcloud auth login`).
3.  **APIs Enabled**:
    ```bash
    gcloud services enable run.googleapis.com cloudbuild.googleapis.com
    ```

## Quick Deployment

We have provided a `deploy.sh` script to automate the build and deploy process.

1.  **Make the script executable**:
    ```bash
    chmod +x deploy.sh
    ```

2.  **Set your Project ID**:
    ```bash
    export GOOGLE_CLOUD_PROJECT=your-project-id
    gcloud config set project $GOOGLE_CLOUD_PROJECT
    ```

3.  **Run the script**:
    ```bash
    ./deploy.sh
    ```

## Data Persistence (Important)

By default, Cloud Run containers are **stateless**. This means if the container restarts, **you will lose your database (`jobs.db`)**.

To persist data, you have two main low-cost options:

### Option A: Cloud Storage FUSE (Cheapest)
Mount a Google Cloud Storage bucket as a file system.
*Note: SQLite on GCS has performance limitations and locking risks, but is fine for a single-user scraper.*

1.  **Create a Bucket**:
    ```bash
    gcloud storage buckets create gs://${GOOGLE_CLOUD_PROJECT}-data --location=us-central1
    ```

2.  **Deploy with Volume Mount**:
    ```bash
    gcloud run deploy linkedin-scraper-resume \
        --image gcr.io/${GOOGLE_CLOUD_PROJECT}/linkedin-scraper-resume \
        --add-volume=name=gcs-data,type=cloud-storage,bucket=${GOOGLE_CLOUD_PROJECT}-data \
        --add-volume-mount=volume=gcs-data,mount-path=/app/data \
        --execution-environment=gen2
    ```

### Option B: Cloud SQL (Robust)
Use a managed PostgreSQL instance. This is more expensive (~$10-30/mo) but robust.
*Requires changing `database.py` to use SQLAlchemy/Postgres instead of SQLite.*

## Environment Variables

You can set environment variables in the Cloud Run console or via CLI:

- `GEMINI_API_KEY`: **Required** for CV generation.
- `LINKEDIN_USERNAME`: Optional (if you want to pre-configure).
- `LINKEDIN_PASSWORD`: Optional.

To set these after deployment:
```bash
gcloud run services update linkedin-scraper-resume \
    --set-env-vars="GEMINI_API_KEY=your_key_here"
```
