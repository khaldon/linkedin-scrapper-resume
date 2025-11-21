# 🚀 Supabase Setup Guide

This guide will help you set up a free **Supabase** (PostgreSQL) database for your application.

## 1. Create a Supabase Project

1. Go to [Supabase.com](https://supabase.com/) and sign up (free).
2. Click **"New Project"**.
3. Choose your organization and name your project (e.g., `linkedin-scraper`).
4. **IMPORTANT:** Set a strong **Database Password** and save it! You will need it later.
5. Choose a region close to you.
6. Click **"Create new project"**.

## 2. Get Your Connection String

1. Once your project is created (takes ~1 minute), go to **Project Settings** (gear icon at the bottom left).
2. Click on **"Database"** in the sidebar.
3. Scroll down to the **"Connection string"** section.
4. Click on the **"URI"** tab.
5. Copy the connection string. It looks like this:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xyzproject.supabase.co:5432/postgres
   ```

## 3. Configure Your App

1. Open your `.env` file in the project root.
2. Add (or update) the `SUPABASE_DATABASE_URL` variable:

   ```env
   SUPABASE_DATABASE_URL=postgresql://postgres:mypassword123@db.xyzproject.supabase.co:5432/postgres
   ```
   *(Replace `[YOUR-PASSWORD]` with the password you created in step 1)*.

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
