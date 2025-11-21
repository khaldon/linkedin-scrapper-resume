# 🔧 Fix Applied: Resilient Database Connection

## Problem
Your application was **crashing on Hugging Face Spaces** startup due to:
```
❌ Postgres connection failed: Network is unreachable
ERROR: Application startup failed. Exiting.
```

The issue: **IPv6 connectivity problems** between HF Spaces and Supabase.

## Solution Applied

### 1. ✅ Automatic Fallback to SQLite

Updated `src/database.py` to gracefully handle connection failures:

**Before:**
```python
# Would crash if PostgreSQL connection failed
self._init_db()
```

**After:**
```python
if self.use_postgres:
    try:
        self._init_db()
        logger.info("✅ Successfully connected to PostgreSQL")
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        logger.warning(f"⚠️  Falling back to SQLite: {self.db_path}")
        self.use_postgres = False
        self._init_db()  # Retry with SQLite
```

**Result:** Your app will **always start**, even if Supabase is unreachable.

### 2. ✅ Connection Timeout

Added timeout to prevent hanging connections:

```python
return psycopg2.connect(
    self.db_url,
    connect_timeout=10,  # 10 second timeout
    options='-c statement_timeout=30000'  # 30 second query timeout
)
```

**Result:** Fast failure instead of hanging indefinitely.

### 3. ✅ Better Logging

Enhanced logging to show what's happening:
- `🚀 Attempting to use Supabase/PostgreSQL Database`
- `✅ Successfully connected to PostgreSQL` (on success)
- `⚠️ Falling back to SQLite` (on failure)

## What This Means for You

### Immediate Effect
✅ **Your app will now start on HF Spaces** even if Supabase is unreachable  
✅ **No more startup crashes**  
✅ **Automatic fallback to SQLite** (ephemeral storage)

### Behavior

| Scenario | What Happens |
|----------|--------------|
| Supabase reachable | ✅ Uses PostgreSQL (persistent) |
| Supabase unreachable | ⚠️ Falls back to SQLite (ephemeral) |
| No SUPABASE_DATABASE_URL | 📂 Uses SQLite by default |

## Next Steps to Fix Supabase Connection

### Option 1: Quick Fix - Use SQLite (Temporary)

Remove `SUPABASE_DATABASE_URL` from HF Secrets:
- App will use SQLite
- **Data will be lost on restart** (ephemeral storage)
- Good for testing/demo

### Option 2: Fix Supabase IPv6 Issue (Recommended)

Try these in order:

#### A. Use Supabase Connection Pooler
1. Go to Supabase Dashboard → Settings → Database
2. Find "Connection Pooling" section
3. Copy the **Transaction** pooler connection string
4. Update HF Secret `SUPABASE_DATABASE_URL` with pooler URL:
   ```
   postgresql://postgres.xxx:password@pooler.supabase.co:6543/postgres
   ```

#### B. Force IPv4 Connection
Update your connection string to include IPv4 preference:
```
postgresql://postgres:password@db.project.supabase.co:5432/postgres?options=-c%20client_encoding=UTF8
```

#### C. Use Direct IPv4 Address
1. Find Supabase IPv4:
   ```bash
   nslookup db.ggpyokubpbvnpcpmtnou.supabase.co
   ```
2. Use the IPv4 address in connection string:
   ```
   postgresql://postgres:password@123.45.67.89:5432/postgres
   ```

### Option 3: Alternative Database (If Supabase Doesn't Work)

**Neon.tech** (Recommended alternative):
- Free tier: 0.5 GB storage
- Better IPv4 support
- Great HF compatibility
- Setup: [neon.tech](https://neon.tech)

**Railway.app**:
- $5/month free credit
- Excellent HF compatibility
- Setup: [railway.app](https://railway.app)

## Testing the Fix

### Test Locally
```bash
# Should work without errors
uv run python -c "from src.database import Database; db = Database(); print('✅ Works!')"
```

### Test on HF
1. Push the updated code to HF
2. Check logs - should see either:
   - `✅ Successfully connected to PostgreSQL` (if Supabase works)
   - `⚠️ Falling back to SQLite` (if Supabase unreachable)
3. App should start successfully either way

## Files Updated

1. **`src/database.py`**
   - Added try/except around PostgreSQL initialization
   - Added automatic fallback to SQLite
   - Added connection timeout
   - Enhanced logging

2. **`docs/HF_TROUBLESHOOTING.md`** (NEW)
   - Comprehensive troubleshooting guide
   - Multiple solutions for network issues
   - Alternative database providers
   - Debugging steps

## Verification

Run the verification script:
```bash
uv run python verify_setup.py
```

Should show:
```
✅ Database connection successful
ℹ️  Database type: SQLite (Local)  # or PostgreSQL if Supabase works
⚠️  For production on Hugging Face, configure SUPABASE_DATABASE_URL
```

## Summary

### What Changed
- ✅ Database initialization is now **resilient**
- ✅ App **won't crash** if PostgreSQL is unreachable
- ✅ **Automatic fallback** to SQLite
- ✅ **Better error messages** and logging

### What You Should Do
1. **Push the updated code** to HF Spaces
2. **Try Option 2A** (Supabase pooler) first
3. **Check HF logs** to see if PostgreSQL connects
4. **If still issues**, try Option 3 (alternative database)

### Current Status
✅ **Code is fixed and ready to deploy**  
✅ **App will start successfully on HF**  
⚠️ **May use ephemeral storage** until Supabase connection is fixed

---

**Need help?** Check `docs/HF_TROUBLESHOOTING.md` for detailed solutions!

**Quick test:** Push to HF and check if app starts (it should!)
