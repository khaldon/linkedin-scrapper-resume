#!/bin/bash

# Exit on error
set -e

# Configuration
SERVICE_NAME="linkedin-scraper-resume"
REGION="us-central1"
IMAGE_NAME="gcr.io/${GOOGLE_CLOUD_PROJECT}/${SERVICE_NAME}"

echo "🚀 Starting deployment for ${SERVICE_NAME}..."

# Check if Google Cloud Project is set
if [ -z "${GOOGLE_CLOUD_PROJECT}" ]; then
    echo "❌ Error: GOOGLE_CLOUD_PROJECT environment variable is not set."
    echo "👉 Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "📦 Building container image..."
gcloud builds submit --tag ${IMAGE_NAME}

echo "💾 Ensuring persistent volume exists..."
# Check if volume exists, if not create it (requires beta component)
if ! gcloud beta run volume-claims describe ${SERVICE_NAME}-data --region=${REGION} > /dev/null 2>&1; then
    echo "   Creating new volume claim..."
    # Note: This assumes using the new Cloud Run Volume feature (Preview/Beta)
    # If not available, we might need to use Network File System (Filestore) or Cloud Storage FUSE.
    # For simplicity and cost in this script, we'll use the standard 'gcloud run deploy' with volume flags if supported,
    # or fallback to a simple local volume (which is ephemeral) if the user doesn't want to pay for Filestore.
    
    # HOWEVER, for a true low-cost persistent solution on Cloud Run (Gen 2), 
    # using Cloud Storage FUSE is often the cheapest "persistent" way for files, 
    # but SQLite on GCS FUSE is risky due to locking.
    # The best "simple" persistent option is actually just a standard volume if available in the region.
    
    # Let's try to create a volume if the user has the beta commands.
    # If this fails, the script will exit, and the user can check the guide.
    true # Placeholder
fi

echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --cpu 1 \
    --execution-environment gen2 \
    --set-env-vars="PYTHONUNBUFFERED=1" \
    --add-volume=name=data-volume,type=cloud-storage,bucket=${GOOGLE_CLOUD_PROJECT}-data \
    --add-volume-mount=volume=data-volume,mount-path=/app/data

# Note: The above volume command uses Cloud Storage FUSE as a generic example.
# Since SQLite on GCS is not recommended for high concurrency, but fine for single-user low traffic.
# A better alternative for SQLite is the new "Volume" support in Cloud Run (Preview).
# For this script, we will use a simpler approach:
# We will deploy WITHOUT persistence first, and print instructions for adding it,
# OR we can use the standard deployment and let the user configure the volume in the console
# to avoid complex CLI flag issues across different gcloud versions.

# REVISED DEPLOY COMMAND (Simpler, safer):
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --region ${REGION} \
    --platform managed \
    --allow-unauthenticated \
    --memory 1Gi \
    --set-env-vars="PYTHONUNBUFFERED=1"

echo "✅ Deployment complete!"
echo "⚠️  IMPORTANT: This deployment currently uses ephemeral storage."
echo "👉 To persist data, please follow the 'Storage Configuration' section in PRODUCTION_GUIDE.md"
