# CareerBoost AI - Frontend

This is the frontend application for CareerBoost AI, a LinkedIn Job Scraper & CV Tailor.

## 🚀 Deployment

This frontend is deployed to **Firebase Hosting**.

### Prerequisites

- Firebase CLI installed: `npm install -g firebase-tools`
- Firebase project configured (already set up in `.firebaserc`)

### Deploy to Firebase

```bash
cd frontend
firebase deploy
```

## 🔧 Configuration

The backend API URL is configured in `static/config.js`:

```javascript
const CONFIG = {
    API_URL: "https://MKhaldon-linkedin-scraper-resume.hf.space",
    USE_LOCAL_API: false
};
```

For local development, set `USE_LOCAL_API: true` and ensure your backend is running on `http://localhost:8080`.

## 📁 Structure

```
frontend/
├── static/
│   ├── index.html       # Main application page
│   ├── app.js           # Frontend logic
│   ├── config.js        # API configuration
│   └── test-firebase.html
├── view_report.html     # Job market analysis report viewer
├── firebase.json        # Firebase hosting configuration
└── .firebaserc          # Firebase project configuration
```

## 🔐 Authentication

The frontend uses **Firebase Authentication** with Google OAuth2. Users must sign in to:
- Generate tailored CVs
- Access their scraped jobs

## 🌐 Backend Integration

The frontend communicates with the backend API hosted on Hugging Face Spaces:
- **Backend URL**: https://MKhaldon-linkedin-scraper-resume.hf.space
- **API Endpoints**: `/api/scrape`, `/api/generate-cv`, `/api/stats`, etc.

## 📝 Features

- **Job Scraping**: Scrape LinkedIn job postings anonymously
- **CV Generation**: Generate ATS-optimized, tailored CVs using AI
- **Market Statistics**: Analyze job market trends and in-demand skills
- **Job Management**: View and manage scraped jobs

## 🛠️ Local Development

To test the frontend locally:

1. Start a local server:
   ```bash
   python -m http.server 8000
   ```

2. Open `http://localhost:8000/static/index.html` in your browser

3. Ensure the backend is running or set `API_URL` to the production backend

## 📄 License

MIT License - See LICENSE file in the root directory
