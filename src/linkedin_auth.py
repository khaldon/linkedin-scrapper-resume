import asyncio
import random
import time
from playwright.async_api import async_playwright, Browser, Page, TimeoutError
import logging
from typing import Optional, List, Dict, Any
from .cookies_manager import CookiesManager

logger = logging.getLogger(__name__)


class LinkedInAuth:
    def __init__(self, headless: bool = False, slow_mo: int = 100):
        self.headless = headless
        self.slow_mo = slow_mo
        self.cookies_manager = CookiesManager()
        self.browser: Optional[Browser] = None
        self.context = None

    async def init_browser(self):
        """Initialize browser with human-like settings"""
        playwright = await async_playwright().start()

        # Launch browser with stealth-like settings
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        # Create context with realistic settings
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="America/New_York",
            permissions=["geolocation"],
            java_script_enabled=True,
            bypass_csp=True,
            screen={"width": 1920, "height": 1080},
        )

        # Add stealth script
        await self.context.add_init_script(
            """
            // Remove automation flags
            delete navigator.__proto__.webdriver;
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Mock Chrome
            window.chrome = {
                runtime: {},
                loadTimes: function() {
                    return {
                        requestTime: 0,
                        startLoadTime: 0,
                        commitLoadTime: 0,
                        finishDocumentLoadTime: 0,
                        finishLoadTime: 0,
                        firstPaintTime: 0,
                        firstPaintAfterLoadTime: 0,
                        navigationType: "Other"
                    };
                }
            };
        """
        )

    async def close_browser(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()

    async def human_like_type(
        self, page: Page, selector: str, text: str, delay_range: tuple = (50, 150)
    ):
        """Type text with human-like delays"""
        try:
            await page.wait_for_selector(selector, state="visible", timeout=10000)
            await page.click(selector)

            for char in text:
                await page.type(selector, char)
                delay = random.randint(*delay_range)
                await asyncio.sleep(delay / 1000)
        except Exception as e:
            logger.error(f"Error typing in {selector}: {str(e)}")
            raise

    async def human_like_click(self, page: Page, selector: str):
        """Click with human-like behavior"""
        try:
            await page.wait_for_selector(selector, state="visible", timeout=10000)

            # Move mouse to element first
            element = await page.query_selector(selector)
            if element:
                box = await element.bounding_box()
                if box:
                    x = box["x"] + random.randint(0, int(box["width"]))
                    y = box["y"] + random.randint(0, int(box["height"]))
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.1, 0.3))

            await page.click(selector)
            await asyncio.sleep(random.uniform(0.5, 1.2))
        except Exception as e:
            logger.error(f"Error clicking {selector}: {str(e)}")
            raise

    async def login(self, email: str, password: str) -> bool:
        """Perform human-like LinkedIn login with better error handling"""
        if not self.browser or not self.context:
            await self.init_browser()

        page = await self.context.new_page()

        try:
            logger.info("Navigating to LinkedIn login page...")
            await page.goto(
                "https://www.linkedin.com/login", wait_until="domcontentloaded", timeout=60000
            )
            await asyncio.sleep(random.uniform(1, 2))

            # Check if we're already on a different page (redirected)
            current_url = page.url
            if "feed" in current_url:
                logger.info("Already logged in - redirected to feed")
                cookies = await self.context.cookies()
                self.cookies_manager.save_cookies(cookies)
                return True

            # Type email
            logger.info("Entering email...")
            await self.human_like_type(page, "input#username", email)
            await asyncio.sleep(random.uniform(0.5, 1))

            # Type password
            logger.info("Entering password...")
            await self.human_like_type(page, "input#password", password)
            await asyncio.sleep(random.uniform(0.5, 1))

            # Click sign in button
            logger.info("Clicking sign in button...")
            await self.human_like_click(page, 'button[type="submit"]')

            # Wait for navigation with multiple possible outcomes
            logger.info("Waiting for login to complete...")

            # Wait for either successful login or error
            try:
                # Wait for navigation to feed or check for success indicators
                await page.wait_for_function(
                    """() => {
                        return window.location.href.includes('feed') || 
                               document.querySelector('div.feed-identity-module__actor-meta') ||
                               document.querySelector('button[aria-label="Me"]');
                    }""",
                    timeout=20000,
                )

                logger.info("Login successful!")

                # Additional wait to ensure page is fully loaded
                await asyncio.sleep(2)

                # Get and save cookies
                cookies = await self.context.cookies()
                self.cookies_manager.save_cookies(cookies)

                return True

            except TimeoutError:
                # Check for common error messages
                error_indicators = [
                    "input#username:invalid",
                    "input#password:invalid",
                    "div.alert.alert-danger",
                    "div.login__form--error",
                    "p.login__form--error-message",
                    "span.error",
                    "div.error-message",
                ]

                for indicator in error_indicators:
                    try:
                        element = await page.query_selector(indicator)
                        if element:
                            error_text = await element.text_content()
                            logger.error(f"Login failed - Error found: {error_text}")
                            return False
                    except:
                        continue

                # Check current URL for clues
                current_url = page.url
                logger.error(f"Login timeout. Current URL: {current_url}")

                # Take a screenshot for debugging
                await page.screenshot(path="logs/login_error.png")
                logger.error("Screenshot saved to logs/login_error.png")

                return False

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            # Take screenshot on error
            try:
                await page.screenshot(path="logs/login_exception.png")
                logger.error("Exception screenshot saved to logs/login_exception.png")
            except:
                pass
            return False
        finally:
            await page.close()

    async def is_logged_in(self) -> bool:
        """Check if user is logged in using saved cookies"""
        if not self.cookies_manager.cookies_exist():
            return False

        if not self.browser or not self.context:
            await self.init_browser()

        page = await self.context.new_page()

        try:
            # Load ALL cookies
            cookies = self.cookies_manager.load_cookies()
            if not cookies:
                logger.warning("No cookies loaded")
                return False

            await self.context.add_cookies(cookies)
            logger.info(f"Added {len(cookies)} cookies to context")

            # Navigate to LinkedIn feed directly
            logger.info("Navigating to LinkedIn feed to test cookies...")
            await page.goto(
                "https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=60000
            )
            await asyncio.sleep(3)

            # Check multiple indicators of successful login
            success_indicators = [
                'button[aria-label="Me"]',
                'button[aria-label="My Network"]',
                'a[href="/mynetwork/"]',
                "div.feed-shared-update-v2",
                "div#global-nav",
                'img[alt*="profile"]',
            ]

            for indicator in success_indicators:
                try:
                    element = await page.query_selector(indicator)
                    if element:
                        logger.info(f"✅ Found login indicator: {indicator}")
                        return True
                except Exception as e:
                    continue

            # If we reach here, check what page we're actually on
            current_url = page.url
            page_title = await page.title()
            logger.warning(
                f"❌ Not logged in. Current URL: {current_url}, Title: {page_title}"
            )

            # Take screenshot for debugging
            await page.screenshot(path="logs/cookie_test_failed.png")
            logger.info("📸 Screenshot saved to logs/cookie_test_failed.png")

            return False

        except Exception as e:
            logger.error(f"❌ Error checking login status: {str(e)}")
            return False
        finally:
            await page.close()

    async def get_authenticated_context(self):
        """Get a context with valid authentication"""
        if await self.is_logged_in():
            return self.context
        else:
            logger.error("Not authenticated. Please login first.")
            return None
