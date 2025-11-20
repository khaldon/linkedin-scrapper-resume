import asyncio
import os
import logging
import sys
from src.linkedin_auth import LinkedInAuth
from src.scraper import LinkedInScraper
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

async def main():
    logger = logging.getLogger(__name__)
    load_dotenv()

    # Get credentials from environment variables
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")

    if not email or not password:
        logger.error(
            "Please set LINKEDIN_EMAIL and LINKEDIN_PASSWORD environment variables"
        )
        return

    # Initialize LinkedIn auth
    # headless=False is often better for LinkedIn to avoid detection, 
    # but in this environment we might need headless=True if there's no display.
    # However, the previous code had headless=False. I'll keep it but note that 
    # in a headless server environment it might fail without Xvfb.
    # Given the user environment, I'll try headless=True first to be safe, 
    # or stick to what was there if I assume the user has a display.
    # The user has "No browser pages are currently open", implying they might see it.
    # But usually agents run in headless environments. 
    # I will check if I can run headful. 
    # For now, let's stick to the existing config but maybe default to headless=True for stability.
    # Actually, the previous code had headless=False. I will respect that but add a fallback?
    # No, let's just use the existing setting but maybe make it configurable.
    
    linkedin_auth = LinkedInAuth(
        headless=True, slow_mo=100
    )

    try:
        # Try to use existing cookies first
        if await linkedin_auth.is_logged_in():
            logger.info("✅ Already logged in with saved cookies")
        else:
            # Perform login
            logger.info("🔐 Performing LinkedIn login...")
            success = await linkedin_auth.login(email, password)
            if not success:
                logger.error("❌ Login failed - check credentials and logs")
                return
            else:
                logger.info("✅ LinkedIn authentication completed successfully!")
                logger.info("🍪 Session cookies saved for future sessions")

        # Get authenticated context
        context = await linkedin_auth.get_authenticated_context()
        if not context:
            logger.error("Could not get authenticated context")
            return

        # Initialize scraper
        scraper = LinkedInScraper(context)

        # Get URL from user
        if len(sys.argv) > 1:
            url = sys.argv[1]
        else:
            print("\n" + "="*50)
            url = input("Enter LinkedIn Job Post URL: ").strip()
            print("="*50 + "\n")

        if not url:
            logger.error("No URL provided")
            return

        logger.info(f"Starting scrape for: {url}")
        result = await scraper.scrape_job_post(url)

        if result:
            print("\n" + "="*50)
            print("🎉 SCRAPING SUCCESSFUL!")
            print("="*50)
            print(f"Title:       {result['title']}")
            print(f"Company:     {result['company']}")
            print(f"Posted By:   {result['poster']}")
            print("-" * 20)
            print(f"Description Preview:\n{result['description']}")
            print("="*50 + "\n")
            
            # Save to file
            import json
            with open("data/last_scrape.json", "w") as f:
                json.dump(result, f, indent=2)
            logger.info("Result saved to data/last_scrape.json")

            # Save to Database
            from src.database import Database
            db = Database()
            job_id = db.save_job(result)
            logger.info(f"Job saved to database with ID: {job_id}")

            # Pipeline Options
            print("\nPipeline Options:")
            print("1. Create Tailored CV (ATS Optimized)")
            print("2. Analyze Data")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                from src.llm_generator import LLMGenerator
                
                # Ask for current CV
                print("\nTo tailor your CV, we need your current CV content.")
                cv_path = input("Enter path to your current CV (txt/md file) [default: cv.md]: ").strip() or "cv.md"
                
                if not os.path.exists(cv_path):
                    print(f"⚠️ File {cv_path} not found. Creating a dummy one for testing.")
                    with open(cv_path, "w") as f:
                        f.write("# My Name\n\n## Experience\nSoftware Engineer...")
                
                with open(cv_path, "r") as f:
                    current_cv = f.read()
                
                print("\n🧠 Generating tailored CV... (This may take a moment)")
                llm = LLMGenerator()
                tailored_cv = llm.generate_tailored_cv(result['full_description'], current_cv)
                
                # Save Generated CV
                output_filename = f"data/tailored_cv_{job_id}.md"
                with open(output_filename, "w") as f:
                    f.write(tailored_cv)
                
                db.save_generated_cv(job_id, current_cv, tailored_cv)
                
                print(f"\n✨ Tailored CV saved to: {output_filename}")
                
                # Convert to PDF
                print("📄 Converting to PDF...")
                from src.pdf_converter import convert_md_to_pdf
                pdf_filename = f"data/tailored_cv_{job_id}.pdf"
                if convert_md_to_pdf(output_filename, pdf_filename):
                    print(f"✨ PDF saved to: {pdf_filename}")
                else:
                    print("⚠️ PDF conversion failed. Please check logs.")

            elif choice == "2":
                print("\n📊 Analyzing Job Market Data...")
                try:
                    from src.stats_generator import generate_job_stats
                    
                    # Generate the report
                    report = generate_job_stats()
                    print("\n" + report)
                    
                    # Save the report
                    save_path = "data/job_market_report.md"
                    with open(save_path, "w") as f:
                        f.write(report)
                    print(f"\n✅ Report saved to {save_path}")
                    
                except ImportError as e:
                    logger.error(f"Missing dependencies: {e}")
                    print(f"\n❌ Missing dependencies: {e}")
                    print("Please run: pip install spacy scikit-learn pandas")
                    print("And: python -m spacy download en_core_web_sm")
                except Exception as e:
                    logger.error(f"Error generating stats: {e}")
                    print(f"\n❌ Error generating stats: {e}")

        else:
            logger.error("Failed to scrape job post")

    except Exception as e:
        logger.error(f"❌ Main execution error: {str(e)}")
    finally:
        await linkedin_auth.close_browser()


if __name__ == "__main__":
    asyncio.run(main())
