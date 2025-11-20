# Deploying to Hugging Face Spaces 🚀

This guide explains how to deploy the `linkedin-scraper-resume` application to **Hugging Face Spaces** for free hosting.

## Prerequisites

1.  **Hugging Face Account**: [Sign up here](https://huggingface.co/join) (it's free!).
2.  **GitHub Account**: You already have this.

## Step 1: Create a New Space

1.  Go to [huggingface.co/spaces](https://huggingface.co/spaces).
2.  Click **"Create new Space"**.
3.  **Name**: `linkedin-scraper-resume` (or similar).
4.  **License**: `MIT`.
5.  **SDK**: Select **Docker**.
6.  **Space Hardware**: Select **Free** (CPU basic).
7.  **Visibility**: Public or Private (your choice).
8.  Click **"Create Space"**.

## Step 2: Connect to GitHub

Once the Space is created, you'll see instructions. We want to mirror your GitHub repo.

1.  In your Space, go to **Settings**.
2.  Scroll down to **"Git Repository"**.
3.  Connect your GitHub repository: `khaldon/linkedin-scrapper-resume`.
    *   *Note: You might need to authorize Hugging Face to access your GitHub.*

**Alternative (Push directly to HF):**
If you prefer not to link repos, you can add the Space as a remote:
```bash
git remote add space https://huggingface.co/spaces/YOUR_HF_USERNAME/linkedin-scraper-resume
git push space main
```

## Step 3: Configure Environment Variables

Your app needs API keys to work.

1.  In your Space, go to **Settings**.
2.  Scroll to **"Variables and secrets"**.
3.  Add the following **Secrets** (for sensitive data):
    *   `GOOGLE_API_KEY`: Your Gemini API key.
    *   `LINKEDIN_EMAIL`: Your LinkedIn email.
    *   `LINKEDIN_PASSWORD`: Your LinkedIn password.
    *   `DATABASE_PATH`: `/app/data/jobs.db` (Optional, but good practice).

## Step 4: Persistence (Optional)

By default, Spaces restart every 48 hours and lose data. To keep your database:

1.  In **Settings** -> **"Storage"**, you can upgrade to a paid tier for persistent storage.
2.  **OR (Free Workaround)**: Use the "Duplicate Space" feature to restart if it sleeps, but accept that `jobs.db` resets on restart.
    *   *For a personal tool, this is usually fine as you can just re-scrape jobs.*

## Troubleshooting

*   **"Build Failed"**: Check the "Logs" tab in your Space.
*   **"Runtime Error"**: Ensure your API keys are set correctly in Secrets.
