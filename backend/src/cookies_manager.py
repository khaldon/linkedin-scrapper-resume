# src/cookies_manager.py
import json
import os
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class CookiesManager:
    def __init__(self, cookies_file: str = "data/cookies.json"):
        self.cookies_file = cookies_file
        self.cookies_dir = os.path.dirname(cookies_file)
        Path(self.cookies_dir).mkdir(parents=True, exist_ok=True)
    
    def save_cookies(self, cookies: List[Dict[str, Any]]) -> None:
        """Save cookies to file - SAVE ALL COOKIES without filtering"""
        try:
            # DON'T filter cookies - save everything
            # LinkedIn uses multiple domains: .linkedin.com, .www.linkedin.com, etc.
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, indent=2)
            logger.info(f"✅ Saved {len(cookies)} cookies to {self.cookies_file}")
        except Exception as e:
            logger.error(f"❌ Error saving cookies: {str(e)}")
    
    def load_cookies(self) -> List[Dict[str, Any]]:
        """Load cookies from file"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                logger.info(f"✅ Loaded {len(cookies)} cookies from {self.cookies_file}")
                return cookies
            else:
                logger.warning(f"⚠️ No cookies file found at {self.cookies_file}")
                return []
        except Exception as e:
            logger.error(f"❌ Error loading cookies: {str(e)}")
            return []
    
    def cookies_exist(self) -> bool:
        """Check if cookies file exists"""
        exists = os.path.exists(self.cookies_file)
        logger.info(f"🍪 Cookies file exists: {exists}")
        return exists