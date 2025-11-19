#!/usr/bin/env python3
"""
Test script to demonstrate Google Gemini API integration for CV tailoring.
This script reads the scraped job data from JSON and generates a tailored CV.
"""

import os
import json
import logging
from dotenv import load_dotenv
from src.llm_generator import LLMGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """
    Main function to test the LLM integration with Google Gemini API.
    """
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key == "your_google_api_key_here":
        logger.warning("⚠️ GOOGLE_API_KEY not set properly in .env file")
        logger.info("📝 To get your API key:")
        logger.info("   1. Visit: https://makersuite.google.com/app/apikey")
        logger.info("   2. Create a new API key")
        logger.info("   3. Add it to your .env file: GOOGLE_API_KEY=your_actual_key")
        logger.info("\n🔄 Continuing with simulated response for demonstration...\n")
    
    # Load the scraped job data
    json_file = "data/last_scrape.json"
    
    if not os.path.exists(json_file):
        logger.error(f"❌ File not found: {json_file}")
        logger.info("💡 Run the main scraper first to generate job data")
        return
    
    with open(json_file, "r") as f:
        job_data = json.load(f)
    
    logger.info("✅ Loaded job data from JSON")
    logger.info(f"📋 Job Title: {job_data.get('title', 'N/A')}")
    logger.info(f"🏢 Company: {job_data.get('company', 'N/A')}")
    
    # Load current CV
    cv_file = "cv.md"
    if not os.path.exists(cv_file):
        logger.error(f"❌ CV file not found: {cv_file}")
        return
    
    with open(cv_file, "r") as f:
        current_cv = f.read()
    
    logger.info(f"✅ Loaded current CV from {cv_file}")
    
    # Initialize LLM Generator
    logger.info("\n🚀 Initializing Google Gemini API...")
    llm = LLMGenerator()
    
    # Generate tailored CV
    logger.info("\n🧠 Generating tailored CV...")
    logger.info("⏳ This may take 10-30 seconds depending on the API response time...\n")
    
    job_description = job_data.get('full_description', job_data.get('description', ''))
    tailored_cv = llm.generate_tailored_cv(job_description, current_cv)
    
    # Save the result
    output_file = "data/tailored_cv_test.md"
    with open(output_file, "w") as f:
        f.write(tailored_cv)
    
    logger.info(f"\n✨ Tailored CV saved to: {output_file}")
    
    # Display preview
    print("\n" + "="*60)
    print("📄 TAILORED CV PREVIEW (First 500 characters)")
    print("="*60)
    print(tailored_cv[:500])
    print("...")
    print("="*60)
    
    # Convert to PDF (optional)
    try:
        from src.pdf_converter import convert_md_to_pdf
        pdf_file = "data/tailored_cv_test.pdf"
        logger.info("\n📄 Converting to PDF...")
        if convert_md_to_pdf(output_file, pdf_file):
            logger.info(f"✨ PDF saved to: {pdf_file}")
        else:
            logger.warning("⚠️ PDF conversion failed")
    except Exception as e:
        logger.warning(f"⚠️ PDF conversion not available: {str(e)}")
    
    logger.info("\n✅ Test completed successfully!")

if __name__ == "__main__":
    main()
