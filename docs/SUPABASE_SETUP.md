# 🚀 Supabase Setup Guide

This guide will help you set up a free **Supabase** (PostgreSQL) database for your application.

## 1. Create a Supabase Project

1. Go to [Supabase.com](https://supabase.com/) and sign up (free).
2. Click **"New Project"**.
3. Choose your organization and name your project (e.g., `linkedin-scraper`).
4. **IMPORTANT:** Set a strong **Database Password** and save it! You will need it later.
5. Choose a region close to you.
6. Click **"Create new project"**.

## 2. Get Your Supabase Credentials

1. Once your project is created (takes ~1 minute), go to **Project Settings** (gear icon at the bottom left).
2. Click on **"API"** in the sidebar.
3. You'll see two important values:
   - **Project URL**: `https://xyzproject.supabase.co`
   - **anon public key**: A long JWT token starting with `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

4. Copy both values - you'll need them for configuration.

## 3. Create Database Tables

1. In Supabase dashboard, click **SQL Editor** in the sidebar
2. Click **"New query"**
3. Paste and run this SQL to create the required tables:

```sql
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    url TEXT UNIQUE,
    title TEXT,
    company TEXT,
    poster TEXT,
    description TEXT,
    full_description TEXT,
    scraped_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- CV generations table
CREATE TABLE IF NOT EXISTS cv_generations (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT,
    original_cv_content TEXT,
    tailored_cv_content TEXT,
    generated_at TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs (id)
);

-- LinkedIn credentials table
CREATE TABLE IF NOT EXISTS linkedin_credentials (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE,
    encrypted_credentials TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

4. Click **"Run"** to execute the SQL

## 4. Configure Your App

1. Open your `.env` file in the project root.
2. Add the Supabase credentials:

   ```env
   SUPABASE_URL=https://xyzproject.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...your-anon-key
   ```

## 4. Restart the App

Restart your application:
```bash
./run_dev_server.sh
```

## ✅ Verification

The app will automatically detect the `SUPABASE_DATABASE_URL` and switch from SQLite to PostgreSQL.
You will see this in the logs:
```
🚀 Using Supabase/PostgreSQL Database
```

The database tables will be created automatically on the first run.

---

## 🔄 Switching Back to SQLite

If you ever want to go back to the local database, simply comment out the variable in `.env`:

```env
# SUPABASE_DATABASE_URL=...
```

The app will automatically fall back to `data/jobs.db`.
