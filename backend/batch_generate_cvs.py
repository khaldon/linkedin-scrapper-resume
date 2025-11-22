#!/usr/bin/env python3
"""
Batch CV Generator: Generate tailored CVs for multiple job postings
This script processes all jobs in the database and generates tailored CVs for each.
"""

import os
import logging
from dotenv import load_dotenv
from src.database import Database
from src.llm_generator import LLMGenerator
from src.pdf_converter import convert_md_to_pdf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """
    Generate tailored CVs for all jobs in the database.
    """
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        logger.error("❌ GOOGLE_API_KEY not set in .env file")
        logger.info("📝 Get your API key from: https://makersuite.google.com/app/apikey")
        return
    
    # Load current CV
    cv_file = "cv.md"
    if not os.path.exists(cv_file):
        logger.error(f"❌ CV file not found: {cv_file}")
        return
    
    with open(cv_file, "r") as f:
        current_cv = f.read()
    
    logger.info(f"✅ Loaded current CV from {cv_file}")
    
    # Initialize database and LLM
    db = Database()
    llm = LLMGenerator()
    
    # Get all jobs from database
    jobs = db.get_all_jobs()
    
    if not jobs:
        logger.warning("⚠️ No jobs found in database")
        logger.info("💡 Run main.py first to scrape some jobs")
        return
    
    logger.info(f"📊 Found {len(jobs)} job(s) in database")
    
    # Process each job
    for i, job in enumerate(jobs, 1):
        job_id = job['id']
        title = job['title']
        company = job['company']
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing Job {i}/{len(jobs)}")
        logger.info(f"📋 Title: {title}")
        logger.info(f"🏢 Company: {company}")
        logger.info(f"{'='*60}")
        
        # Check if CV already generated
        existing_cv = db.get_generated_cv(job_id)
        if existing_cv:
            logger.info("⏭️  CV already generated for this job. Skipping...")
            continue
        
        # Generate tailored CV
        logger.info("🧠 Generating tailored CV...")
        try:
            tailored_cv = llm.generate_tailored_cv(
                job_description=job['full_description'],
                current_cv=current_cv
            )
            
            # Save to file
            output_file = f"data/tailored_cv_{job_id}.md"
            with open(output_file, "w") as f:
                f.write(tailored_cv)
            
            logger.info(f"✅ Saved to: {output_file}")
            
            # Save to database
            db.save_generated_cv(job_id, current_cv, tailored_cv)
            logger.info("💾 Saved to database")
            
            # Convert to PDF
            pdf_file = f"data/tailored_cv_{job_id}.pdf"
            if convert_md_to_pdf(output_file, pdf_file):
                logger.info(f"📄 PDF saved to: {pdf_file}")
            
        except Exception as e:
            logger.error(f"❌ Error generating CV: {str(e)}")
            continue
    
    logger.info(f"\n{'='*60}")
    logger.info("✅ Batch processing completed!")
    logger.info(f"{'='*60}")

if __name__ == "__main__":
    main()
