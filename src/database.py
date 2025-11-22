import os
import logging
from datetime import datetime
from typing import Dict, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from supabase import create_client, Client

    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    logger.error(
        "❌ Supabase package not installed. Install with: pip install supabase"
    )


def _serialize_datetime(data):
    """Convert datetime objects to ISO format strings for JSON serialization"""
    if isinstance(data, dict):
        return {k: _serialize_datetime(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_serialize_datetime(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    return data


class Database:
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize Supabase database connection.

        Required environment variables:
        - SUPABASE_URL: Your Supabase project URL
        - SUPABASE_KEY: Your Supabase anon/public key

        Raises:
            RuntimeError: If Supabase is not configured or package not installed
        """
        # Check for Supabase configuration
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not HAS_SUPABASE:
            raise RuntimeError(
                "Supabase package is not installed. "
                "Install it with: pip install supabase"
            )

        if not self.supabase_url or not self.supabase_key:
            raise RuntimeError(
                "Supabase configuration missing. "
                "Please set SUPABASE_URL and SUPABASE_KEY environment variables. "
                "See docs/SUPABASE_SETUP.md for setup instructions."
            )

        logger.info("🚀 Connecting to Supabase Database...")
        try:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            # Test connection by checking if we can access the database
            self._verify_supabase_connection()
            logger.info("✅ Successfully connected to Supabase")
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {e}")
            raise RuntimeError(
                f"Failed to connect to Supabase: {e}. "
                "Please check your SUPABASE_URL and SUPABASE_KEY."
            )

    def _verify_supabase_connection(self):
        """Verify Supabase connection by attempting to query"""
        try:
            # Try to query jobs table (will create if doesn't exist via Supabase dashboard)
            self.supabase.table("jobs").select("id").limit(1).execute()
        except Exception:
            # If table doesn't exist, that's okay - we'll create it via SQL
            logger.info("Tables may need to be created in Supabase dashboard")
            pass

    def save_job(self, job_data: Dict) -> int:
        """Save job to database"""
        try:
            # Prepare data for Supabase
            data = {
                "url": job_data["url"],
                "title": job_data["title"],
                "company": job_data["company"],
                "poster": job_data.get("poster"),
                "description": job_data.get("description"),
                "full_description": job_data.get("full_description"),
                "scraped_at": datetime.now().isoformat(),
            }

            # Upsert (insert or update)
            result = (
                self.supabase.table("jobs").upsert(data, on_conflict="url").execute()
            )

            if result.data and len(result.data) > 0:
                return result.data[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Error saving job to Supabase: {e}")
            raise

    def check_job_exists(self, url: str) -> Optional[Dict]:
        """Check if job exists by URL"""
        try:
            result = (
                self.supabase.table("jobs")
                .select("id, title, company, scraped_at")
                .eq("url", url)
                .execute()
            )

            if result.data and len(result.data) > 0:
                return _serialize_datetime(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error checking job in Supabase: {e}")
            return None

    def get_job(self, job_id: int) -> Optional[Dict]:
        """Get job by ID"""
        try:
            result = self.supabase.table("jobs").select("*").eq("id", job_id).execute()

            if result.data and len(result.data) > 0:
                return _serialize_datetime(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting job from Supabase: {e}")
            return None

    def save_generated_cv(self, job_id: int, original_cv: str, tailored_cv: str):
        """Save generated CV"""
        try:
            data = {
                "job_id": job_id,
                "original_cv_content": original_cv,
                "tailored_cv_content": tailored_cv,
                "generated_at": datetime.now().isoformat(),
            }

            self.supabase.table("cv_generations").insert(data).execute()
        except Exception as e:
            logger.error(f"Error saving CV to Supabase: {e}")
            raise

    def get_all_jobs(
        self, limit: int = 10, offset: int = 0, include_description: bool = False
    ) -> List[Dict]:
        """Get all jobs with pagination"""
        try:
            select_query = "id, url, title, company, poster, scraped_at"
            if include_description:
                select_query += ", full_description"

            result = (
                self.supabase.table("jobs")
                .select(select_query)
                .order("scraped_at", desc=True)
                .range(offset, offset + limit - 1)
                .execute()
            )

            # Serialize datetime objects to strings
            return _serialize_datetime(result.data) if result.data else []
        except Exception as e:
            logger.error(f"Error getting jobs from Supabase: {e}")
            return []

    def delete_job(self, job_id: int) -> bool:
        """Delete job and associated CVs"""
        try:
            # Delete CV generations first
            self.supabase.table("cv_generations").delete().eq(
                "job_id", job_id
            ).execute()

            # Delete job
            result = self.supabase.table("jobs").delete().eq("id", job_id).execute()

            return result.data is not None
        except Exception as e:
            logger.error(f"Error deleting job from Supabase: {e}")
            return False

    # User management methods
    def create_user(self, email: str, hashed_password: str) -> int:
        """Create a new user"""
        try:
            data = {
                "email": email,
                "hashed_password": hashed_password,
            }

            result = self.supabase.table("users").insert(data).execute()

            if result.data and len(result.data) > 0:
                return result.data[0]["id"]
            return None
        except Exception as e:
            logger.error(f"Error creating user in Supabase: {e}")
            raise

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            result = (
                self.supabase.table("users").select("*").eq("email", email).execute()
            )

            if result.data and len(result.data) > 0:
                return _serialize_datetime(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting user from Supabase: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        try:
            result = (
                self.supabase.table("users").select("*").eq("id", user_id).execute()
            )

            if result.data and len(result.data) > 0:
                return _serialize_datetime(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Error getting user from Supabase: {e}")
            return None

    # LinkedIn credentials management
    def store_linkedin_credentials(self, user_id: int, encrypted_credentials: str):
        """Store encrypted LinkedIn credentials"""
        try:
            data = {
                "user_id": user_id,
                "encrypted_credentials": encrypted_credentials,
                "updated_at": datetime.now().isoformat(),
            }

            self.supabase.table("linkedin_credentials").upsert(
                data, on_conflict="user_id"
            ).execute()
        except Exception as e:
            logger.error(f"Error storing credentials in Supabase: {e}")
            raise

    def get_linkedin_credentials(self, user_id: int) -> Optional[str]:
        """Get encrypted LinkedIn credentials"""
        try:
            result = (
                self.supabase.table("linkedin_credentials")
                .select("encrypted_credentials")
                .eq("user_id", user_id)
                .execute()
            )

            if result.data and len(result.data) > 0:
                return result.data[0]["encrypted_credentials"]
            return None
        except Exception as e:
            logger.error(f"Error getting credentials from Supabase: {e}")
            return None

    def delete_linkedin_credentials(self, user_id: int) -> bool:
        """Delete LinkedIn credentials"""
        try:
            result = (
                self.supabase.table("linkedin_credentials")
                .delete()
                .eq("user_id", user_id)
                .execute()
            )

            return result.data is not None
        except Exception as e:
            logger.error(f"Error deleting credentials from Supabase: {e}")
            return False
