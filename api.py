from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
import asyncio
import os
import json
from pathlib import Path
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import existing modules
from src.linkedin_auth import LinkedInAuth
from src.scraper import LinkedInScraper
from src.database import Database
from src.llm_generator import LLMGenerator
from src.stats_generator import generate_job_stats
from src.pdf_converter import convert_md_to_pdf
from src.firebase_auth import verify_firebase_token, firebase_auth_manager
from src.encryption import encrypt_linkedin_credentials, decrypt_linkedin_credentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="LinkedIn Job Scraper & CV Tailor",
    description="Scrape LinkedIn jobs and generate tailored CVs with AI - OAuth2 Authenticated",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")

# Security
security = HTTPBearer(auto_error=False)

# Pydantic models
class JobURLRequest(BaseModel):
    url: HttpUrl

class JobResponse(BaseModel):
    job_id: int
    title: str
    company: str
    poster: str
    description: str

class LinkedInCredentials(BaseModel):
    email: str
    password: str

class UserSync(BaseModel):
    uid: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None

# Global state
scraper_instance = None
auth_instance = None

# Dependency to get current user from Firebase token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from Firebase token"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_info = verify_firebase_token(token)
        return user_info
    except HTTPException:
        return None
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return None

# Dependency to require authentication
async def require_auth(user = Depends(get_current_user)):
    """Require authentication"""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting LinkedIn Job Scraper API with Firebase Auth...")
    
    # Create necessary directories
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    
    # Initialize database
    db = Database()
    logger.info("Database initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global auth_instance
    if auth_instance:
        await auth_instance.close_browser()
    logger.info("Shutting down...")

@app.get("/")
async def root():
    """Root endpoint - returns API info"""
    try:
        # Try to serve the HTML file
        html_path = Path("static/index.html")
        if html_path.exists():
            return FileResponse("static/index.html")
        else:
            # Fallback if HTML doesn't exist
            return {
                "message": "LinkedIn Job Scraper & CV Tailor API",
                "version": "2.0.0",
                "endpoints": {
                    "docs": "/docs",
                    "health": "/api/health",
                    "scrape": "/api/scrape",
                    "jobs": "/api/jobs"
                },
                "note": "Visit /docs for full API documentation"
            }
    except Exception as e:
        logger.error(f"Error serving root: {e}")
        return {
            "message": "LinkedIn Job Scraper & CV Tailor API",
            "version": "2.0.0",
            "docs_url": "/docs",
            "error": str(e)
        }

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    return JSONResponse(content={"message": "No favicon"}, status_code=204)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "auth": "Firebase OAuth2"
    }

# Authentication endpoints
@app.post("/api/auth/sync")
async def sync_user(user = Depends(require_auth)):
    """Sync Firebase user with local database"""
    try:
        db = Database()
        
        # Check if user exists
        existing_user = db.get_user_by_email(user['email'])
        
        if not existing_user:
            # Create new user (no password needed for OAuth2)
            user_id = db.create_user(user['email'], hashed_password="oauth2")
            logger.info(f"Created new user: {user['email']}")
        else:
            user_id = existing_user['id']
        
        return {
            "message": "User synced successfully",
            "user_id": user_id,
            "email": user['email']
        }
    except Exception as e:
        logger.error(f"Error syncing user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/linkedin/store-credentials")
async def store_linkedin_credentials(
    credentials: LinkedInCredentials,
    user = Depends(require_auth)
):
    """Store encrypted LinkedIn credentials for a user"""
    try:
        db = Database()
        
        # Get or create user
        existing_user = db.get_user_by_email(user['email'])
        if not existing_user:
            user_id = db.create_user(user['email'], hashed_password="oauth2")
        else:
            user_id = existing_user['id']
        
        # Encrypt credentials
        encrypted = encrypt_linkedin_credentials(
            user['email'],
            credentials.email,
            credentials.password
        )
        
        # Store in database
        db.store_linkedin_credentials(user_id, encrypted)
        
        logger.info(f"Stored encrypted LinkedIn credentials for user: {user['email']}")
        
        return {
            "message": "LinkedIn credentials encrypted and stored successfully",
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error storing credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/linkedin/get-credentials")
async def get_linkedin_credentials(user = Depends(require_auth)):
    """Get decrypted LinkedIn credentials for a user"""
    try:
        db = Database()
        
        existing_user = db.get_user_by_email(user['email'])
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        encrypted = db.get_linkedin_credentials(existing_user['id'])
        if not encrypted:
            raise HTTPException(status_code=404, detail="LinkedIn credentials not found")
        
        # Decrypt credentials
        decrypted = decrypt_linkedin_credentials(user['email'], encrypted)
        if not decrypted:
            raise HTTPException(status_code=500, detail="Failed to decrypt credentials")
        
        return {
            "email": decrypted['email'],
            "has_password": bool(decrypted.get('password'))
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Job scraping endpoints
@app.post("/api/scrape", response_model=JobResponse)
async def scrape_job(request: JobURLRequest, user = Depends(get_current_user)):
    """Scrape a LinkedIn job posting"""
    global auth_instance, scraper_instance
    
    try:
        db = Database()
        linkedin_email = None
        linkedin_password = None
        
        # Try to get stored credentials if user is authenticated
        if user:
            existing_user = db.get_user_by_email(user['email'])
            if existing_user:
                encrypted = db.get_linkedin_credentials(existing_user['id'])
                if encrypted:
                    decrypted = decrypt_linkedin_credentials(user['email'], encrypted)
                    if decrypted:
                        linkedin_email = decrypted['email']
                        linkedin_password = decrypted['password']
        
        # Fallback to environment variables
        if not linkedin_email:
            linkedin_email = os.getenv("LINKEDIN_EMAIL")
            linkedin_password = os.getenv("LINKEDIN_PASSWORD")
        
        if not linkedin_email or not linkedin_password:
            raise HTTPException(
                status_code=500,
                detail="LinkedIn credentials not configured. Please store your credentials in the LinkedIn Auth tab."
            )
        
        # Initialize auth if needed
        if not auth_instance:
            auth_instance = LinkedInAuth(headless=True, slow_mo=100)
            
            if not await auth_instance.is_logged_in():
                success = await auth_instance.login(linkedin_email, linkedin_password)
                if not success:
                    raise HTTPException(
                        status_code=401,
                        detail="LinkedIn authentication failed"
                    )
        
        # Get authenticated context
        context = await auth_instance.get_authenticated_context()
        if not context:
            raise HTTPException(
                status_code=500,
                detail="Could not get authenticated context"
            )
        
        # Initialize scraper
        scraper_instance = LinkedInScraper(context)
        
        # Scrape the job
        result = await scraper_instance.scrape_job_post(str(request.url))
        
        if not result:
            raise HTTPException(
                status_code=404,
                detail="Failed to scrape job posting"
            )
        
        # Save to database
        job_id = db.save_job(result)
        
        return JobResponse(
            job_id=job_id,
            title=result['title'],
            company=result['company'],
            poster=result['poster'],
            description=result['description'][:500] + "..."
        )
        
    except Exception as e:
        logger.error(f"Error scraping job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-cv")
async def generate_cv(
    job_id: int = Form(...),
    cv_file: UploadFile = File(...),
    user = Depends(get_current_user)
):
    """Generate a tailored CV for a job"""
    try:
        # Read uploaded CV
        cv_content = await cv_file.read()
        current_cv = cv_content.decode('utf-8')
        
        # Get job from database
        db = Database()
        job = db.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Generate tailored CV
        llm = LLMGenerator()
        tailored_cv = llm.generate_tailored_cv(job['full_description'], current_cv)
        
        # Save CV
        cv_filename = f"data/tailored_cv_{job_id}.md"
        with open(cv_filename, "w") as f:
            f.write(tailored_cv)
        
        # Convert to PDF
        pdf_filename = f"data/tailored_cv_{job_id}.pdf"
        convert_md_to_pdf(cv_filename, pdf_filename)
        
        # Save to database
        db.save_generated_cv(job_id, current_cv, tailored_cv)
        
        return {
            "job_id": job_id,
            "cv_markdown": f"/data/tailored_cv_{job_id}.md",
            "cv_pdf": f"/data/tailored_cv_{job_id}.pdf",
            "message": "CV generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating CV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats(user = Depends(get_current_user)):
    """Get job market statistics"""
    try:
        stats_file = Path("data/stats_data.json")
        
        if not stats_file.exists():
            generate_job_stats()
        
        with open(stats_file, 'r') as f:
            stats_data = json.load(f)
        
        return stats_data
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stats/generate")
async def generate_stats(user = Depends(get_current_user)):
    """Generate fresh job market statistics"""
    try:
        report = generate_job_stats()
        
        with open("data/stats_data.json", 'r') as f:
            stats_data = json.load(f)
        
        return {
            "message": "Statistics generated successfully",
            "stats": stats_data,
            "charts": {
                "technologies": "/data/chart_technologies.png",
                "languages": "/data/chart_languages.png",
                "soft_skills": "/data/chart_soft_skills.png",
                "hard_skills": "/data/chart_hard_skills.png"
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs")
async def list_jobs(limit: int = 10, offset: int = 0, user = Depends(get_current_user)):
    """List all scraped jobs"""
    try:
        db = Database()
        jobs = db.get_all_jobs(limit=limit, offset=offset)
        
        return {
            "jobs": jobs,
            "total": len(jobs),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: int, user = Depends(get_current_user)):
    """Get a specific job by ID"""
    try:
        db = Database()
        job = db.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return job
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: int, user = Depends(require_auth)):
    """Delete a job"""
    try:
        db = Database()
        success = db.delete_job(job_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return {"message": "Job deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
