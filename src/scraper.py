import logging
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional

logger = logging.getLogger(__name__)

class LinkedInScraper:
    """
    LinkedIn job scraper that works WITHOUT authentication.
    Scrapes publicly visible job post data only (as anonymous user).
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
    
    @staticmethod
    def normalize_linkedin_url(url: str) -> str:
        """
        Normalize LinkedIn job URLs to canonical format: https://www.linkedin.com/jobs/view/{job_id}
        
        Handles various URL formats:
        - https://www.linkedin.com/jobs/view/4284088753
        - https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4284088753
        - https://www.linkedin.com/jobs/search/?currentJobId=4284088753
        
        Args:
            url: LinkedIn job URL in any format
            
        Returns:
            Canonical URL format
        """
        import re
        from urllib.parse import urlparse, parse_qs
        
        # Extract job ID from URL
        job_id = None
        
        # Method 1: Extract from /jobs/view/{id} format
        match = re.search(r'/jobs/view/(\d+)', url)
        if match:
            job_id = match.group(1)
        
        # Method 2: Extract from currentJobId parameter
        if not job_id:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            if 'currentJobId' in params:
                job_id = params['currentJobId'][0]
        
        # Method 3: Extract any sequence of digits after /jobs/
        if not job_id:
            match = re.search(r'/jobs/[^/]*/(\d+)', url)
            if match:
                job_id = match.group(1)
        
        if job_id:
            canonical_url = f"https://www.linkedin.com/jobs/view/{job_id}"
            logger.info(f"🔗 Normalized URL: {url} → {canonical_url}")
            return canonical_url
        else:
            logger.warning(f"⚠️ Could not extract job ID from URL: {url}. Using as-is.")
            return url
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def start(self):
        """Initialize browser"""
        if not self.browser:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            logger.info("✅ Browser initialized for anonymous scraping")
    
    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            logger.info("✅ Browser closed")

    async def scrape_job_post(self, url: str) -> Optional[dict]:
        """
        Scrape a LinkedIn job post anonymously (no login required).
        Only publicly visible data will be extracted.
        
        Args:
            url: LinkedIn job post URL (any format)
            
        Returns:
            Dictionary with job details or None if scraping failed
        """
        # Normalize URL to canonical format
        url = self.normalize_linkedin_url(url)
        
        if not self.browser:
            await self.start()
        
        # Create a new context for each scrape (isolated session)
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        try:
            logger.info(f"🔍 Scraping job post anonymously: {url}")
            
            # Navigate to job post
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)  # Wait for dynamic content
            
            # Get page title for fallback
            page_title = await page.title()
            logger.info(f"📄 Page Title: {page_title}")
            
            # Parse title and company from page title
            # Format: "Job Title | Company | LinkedIn" or "Job Title | Company"
            meta_title = None
            meta_company = None
            if "|" in page_title:
                parts = page_title.split("|")
                if len(parts) >= 2:
                    meta_title = parts[0].strip()
                    meta_company = parts[1].strip()

            # Extract Title
            logger.info("📋 Extracting job title...")
            title = await self._get_text(page, [
                "h1.job-details-jobs-unified-top-card__job-title",
                "h1.top-card-layout__title",
                ".job-details-jobs-unified-top-card__job-title h1",
                "h1.topcard__title",
                "h1",
                '[data-testid="job-title"]'
            ])
            
            if not title and meta_title:
                logger.info(f"Using fallback title from metadata: {meta_title}")
                title = meta_title

            # Extract Description
            logger.info("📝 Extracting job description...")
            try:
                # Try to click "See more" button if it exists
                see_more = await page.query_selector("button.jobs-description__footer-button")
                if see_more:
                    await see_more.click()
                    await page.wait_for_timeout(1000)
            except:
                pass

            description = await self._get_text(page, [
                "div.jobs-description__content",
                "div.show-more-less-html__markup",
                "#job-details",
                '[data-testid="expandable-text-box"]',
                ".description__text",
                ".jobs-box__html-content"
            ])

            # Extract Poster (may not be available anonymously)
            logger.info("👤 Extracting poster info...")
            poster = await self._get_text(page, [
                ".jobs-poster__name",
                ".message-the-hiring-team__name",
                ".hirer-card__hirer-information",
                '[data-testid="hirer-card"]'
            ])
            
            if not poster:
                poster = "Not publicly available"
            
            # Extract Company
            logger.info("🏢 Extracting company name...")
            company = await self._get_text(page, [
                ".job-details-jobs-unified-top-card__company-name",
                ".topcard__org-name-link",
                "a.app-aware-link",
                'a[href*="/company/"]',
                ".jobs-unified-top-card__company-name"
            ])
            
            if not company and meta_company:
                logger.info(f"Using fallback company from metadata: {meta_company}")
                company = meta_company

            # Validate we got minimum required data
            if not title or not description:
                logger.error("❌ Failed to extract minimum required data (title or description)")
                return None

            logger.info(f"✅ Successfully scraped: {title} at {company}")

            return {
                "title": title,
                "description": description[:500] + "..." if len(description) > 500 else description,
                "full_description": description,
                "poster": poster,
                "company": company or "Unknown",
                "url": url
            }

        except Exception as e:
            logger.error(f"❌ Error scraping job post: {str(e)}")
            try:
                await page.screenshot(path="logs/scraping_error.png")
                logger.info("📸 Screenshot saved to logs/scraping_error.png")
            except:
                pass
            return None
            
        finally:
            await page.close()
            await context.close()

    async def _get_text(self, page: Page, selectors: list) -> Optional[str]:
        """Try multiple selectors and return first matching text"""
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.inner_text()
                    if text:
                        return text.strip()
            except:
                continue
        return None
