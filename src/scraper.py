import logging
from playwright.async_api import BrowserContext, Page

logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self, context: BrowserContext):
        self.context = context

    async def scrape_job_post(self, url: str):
        page = await self.context.new_page()
        try:
            logger.info(f"Navigating to {url}...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)  # Wait for dynamic content

            # Get page title for fallback
            page_title = await page.title()
            logger.info(f"Page Title: {page_title}")
            
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
            logger.info("Extracting job title...")
            title = await self._get_text(page, [
                "h1.job-details-jobs-unified-top-card__job-title",
                "h1.top-card-layout__title",
                ".job-details-jobs-unified-top-card__job-title h1",
                "h1",
                '[data-testid="job-title"]'
            ])
            
            if not title and meta_title:
                logger.info(f"Using fallback title from metadata: {meta_title}")
                title = meta_title

            # Extract Description
            logger.info("Extracting job description...")
            try:
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
                ".description__text"
            ])

            # Extract Poster
            logger.info("Extracting poster info...")
            poster = await self._get_text(page, [
                ".jobs-poster__name",
                ".message-the-hiring-team__name",
                ".hirer-card__hirer-information",
                '[data-testid="hirer-card"]'
            ])
            
            if not poster:
                # Try finding "People you can reach out to" section
                try:
                    # Find h2 with specific text
                    h2 = page.locator('h2', has_text="People you can reach out to")
                    if await h2.count() > 0:
                        # Get the container following the h2
                        # Usually it's a sibling div
                        container = h2.locator("xpath=following-sibling::div")
                        if await container.count() > 0:
                            # Look for a name inside. Usually the first strong text or link
                            # Based on HTML dump: <a href="...">...</a> ... <p>Name</p>
                            # Or just get all text and take the first line
                            text = await container.first.inner_text()
                            if text:
                                lines = text.split('\n')
                                # The first line is often the name
                                poster = lines[0].strip()
                                logger.info(f"Found poster from 'People you can reach out to': {poster}")
                except Exception as e:
                    logger.warning(f"Error extracting poster from section: {e}")
            
            # Extract Company
            company = await self._get_text(page, [
                ".job-details-jobs-unified-top-card__company-name",
                ".topcard__org-name-link",
                "a.app-aware-link.new-top-card-cl-data-id-link",
                'a[href*="/company/"]'
            ])
            
            if not company and meta_company:
                logger.info(f"Using fallback company from metadata: {meta_company}")
                company = meta_company

            return {
                "title": title,
                "description": description[:500] + "..." if description else None,
                "full_description": description,
                "poster": poster,
                "company": company,
                "url": url
            }

        except Exception as e:
            logger.error(f"Error scraping job post: {str(e)}")
            await page.screenshot(path="logs/scraping_error.png")
            return None
        finally:
            await page.close()

    async def _get_text(self, page: Page, selectors: list):
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
