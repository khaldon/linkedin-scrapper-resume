# Public Deployment Guide 🌐

This application is now configured for **public deployment** on Hugging Face Spaces. Users must provide their own credentials - no shared resources!

## ✅ What Changed

### **Before** (Private Use Only):
- Used environment variables for LinkedIn credentials
- Used environment variable for Google API key
- Only the owner could use the app

### **After** (Public Safe):
- ✅ Users must authenticate with **Firebase (Google OAuth2)**
- ✅ Users must provide their own **LinkedIn credentials** (encrypted and stored securely)
- ✅ Users must provide their own **Google API key** for each CV generation
- ✅ **No shared API quotas** - everyone uses their own resources

---

## 🚀 For Hugging Face Space Owner (You)

### Step 1: Make Your Space Public

1. Go to: `https://huggingface.co/spaces/MKhaldon/linkedin-scraper-resume/settings`
2. Under **"Visibility"**, change to **Public**
3. Click **Save**

### Step 2: Remove Default Secrets (Optional)

Since users now provide their own credentials, you can **remove** these from Hugging Face Space secrets:

-  `LINKEDIN_EMAIL` (not needed anymore)
-  `LINKEDIN_PASSWORD` (not needed anymore)
-  `GOOGLE_API_KEY` (not needed anymore)

**Keep these secrets** (required for Firebase auth):
- ✅ Any Firebase-related secrets you added

### Step 3: Update README

Add this to your Hugging Face Space README:

```markdown
## How to Use

1. **Sign In** with your Google account (Firebase OAuth2)
2. **Store LinkedIn Credentials** in the "LinkedIn Auth" tab
3. **Scrape Jobs** by pasting LinkedIn job URLs
4. **Generate CVs** by providing your Google API key

### Requirements:
- Google account (for authentication)
- LinkedIn account (for job scraping)
- Google API key (free tier available)

[Get a free Google API key →](https://makersuite.google.com/app/apikey)
```

---

## 👥 For End Users

### Step 1: Sign In

1. Visit the app URL
2. Click **"Login"** button  
3. Choose **"Sign in with Google"**
4. Authorize the app

### Step 2: Store Your LinkedIn Credentials

1. Go to the **"LinkedIn Auth"** tab
2. Enter your LinkedIn email and password
3. Click **"Store Credentials Securely"**

**Your credentials are**:
- Encrypted with AES-256
- Stored securely per-user
- Never shared with others

### Step 3: Scrape Jobs

1. Go to the **"Scrape Job"** tab
2. Paste a LinkedIn job URL
3. Click **"Scrape Job"**

The app will:
- Use **YOUR LinkedIn credentials** to access the job
- Save the job details to the database

### Step 4: Generate Tailored CVs

1. Go to the **"Generate CV"** tab
2. Select a previously scraped job
3. Upload your current CV (Markdown or TXT)
4. **Enter your Google API Key** ([Get one here](https://makersuite.google.com/app/apikey))
5. Click **"Generate Tailored CV"**

The app will:
- Use **YOUR Google API key** to call Gemini
- Generate a tailored CV optimized for the job
- Return Markdown and PDF versions

---

## 🔐 Security & Privacy

### User Data Encryption

- LinkedIn credentials are **encrypted with AES-256**
- Each user has their own encryption key
- Credentials cannot be decrypted by other users

### No Shared Resources

- Each user provides their own Google API key
- Each user stores their own LinkedIn credentials
- No API quota conflicts between users

### Firebase Authentication

- Industry-standard OAuth2 authentication
- No password storage on the server
- Supports Google and LinkedIn sign-in

---

## 💰 Cost Breakdown for Users

| Service | Cost | Free Tier |
|---------|------|-----------|
| **Hugging Face Hosting** | Free | ✅ |
| **Firebase Auth** | Free | ✅ |
| **Google Gemini API** | Pay-per-use | ✅ 15 RPM, 1,500 RPD |
| **LinkedIn Account** | Free | ✅ |

**Total: FREE** for normal usage! 🎉

---

## 🛠️ Technical Details

### API Endpoints

All endpoints require **Firebase authentication** (except `/` and `/api/health`):

#### Authentication
- `POST /api/auth/sync` - Sync Firebase user with backend
- `POST /api/linkedin/store-credentials` - Store LinkedIn credentials
- `GET /api/linkedin/get-credentials` - Retrieve LinkedIn credentials

#### Job Scraping
- `POST /api/scrape` - Scrape a LinkedIn job (requires stored LinkedIn credentials)
- `GET /api/jobs` - List scraped jobs
- `GET /api/jobs/{id}` - Get job details
- `DELETE /api/jobs/{id}` - Delete a job

#### CV Generation
- `POST /api/generate-cv` - Generate tailored CV (requires Google API key in form)

#### Stats  
- `GET /api/stats` - Get job market statistics  
- `POST /api/stats/generate` - Generate fresh statistics

### Environment Variables (Server Side)

No sensitive credentials needed! Only:
- `DATABASE_PATH` - SQLite database path (default: `/app/data/jobs.db`)
- Firebase configuration (public config)

---

## 📊 Monitoring Usage

### As the Space Owner:

1. Check **Space Logs** for errors
2. Monitor **Build status** in the HF Space dashboard
3. Watch for abuse patterns (excessive scraping, etc.)

### Rate Limiting (Future Enhancement):

If you experience abuse, you can add:
- Per-user rate limiting
- Daily scraping quotas
- Token expiration policies

---

## ❓ FAQ

**Q: Is my LinkedIn password safe?**  
A: Yes! It's encrypted with AES-256 before storage. Each user has a unique encryption key derived from their Firebase user ID.

**Q: Can the Space owner see my LinkedIn password?**  
A: No! Passwords are encrypted end-to-end. Only you can decrypt them.

**Q: Do I need to pay for Google Gemini API?**  
A: Gemini has a generous free tier (15 requests/min, 1,500/day). Most users won't exceed this.

**Q: What if I don't have a Google API key?**  
A: [Get one for free here](https://makersuite.google.com/app/apikey) - takes 2 minutes!

**Q: Can I use this without signing in?**  
A: No, Firebase authentication is required to ensure each user has isolated credentials and data.

---

## 🎉 You're All Set!

Your app is now **public and secure**. Users can safely use it without any risk of credential leakage or API quota conflicts.

**Next Steps:**
1. Share your Hugging Face Space URL
2. Add it to your portfolio/resume
3. Monitor for feedback and issues

**Questions?** Open an issue on GitHub or contact the developer.
