import sqlite3
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
    logger.warning(
        "⚠️  Supabase package not installed. Install with: pip install supabase"
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
        # Check for Supabase configuration
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.use_supabase = bool(
            self.supabase_url and self.supabase_key and HAS_SUPABASE
        )

        # Set SQLite path as fallback
        if db_path is None:
            self.db_path = os.getenv("DATABASE_PATH", "data/jobs.db")
        else:
            self.db_path = db_path

        if self.use_supabase:
            logger.info("🚀 Attempting to use Supabase Database")
            try:
                self.supabase: Client = create_client(
                    self.supabase_url, self.supabase_key
                )
                # Test connection by checking if we can access the database
                self._verify_supabase_connection()
                logger.info("✅ Successfully connected to Supabase")
            except Exception as e:
                logger.error(f"❌ Supabase connection failed: {e}")
                logger.warning(f"⚠️  Falling back to SQLite: {self.db_path}")
                self.use_supabase = False
                self._init_sqlite()
        else:
            logger.info(f"📂 Using Local SQLite: {self.db_path}")
            self._init_sqlite()

    def _verify_supabase_connection(self):
        """Verify Supabase connection by attempting to query"""
        try:
            # Try to query jobs table (will create if doesn't exist via Supabase dashboard)
            self.supabase.table("jobs").select("id").limit(1).execute()
        except Exception:
            # If table doesn't exist, that's okay - we'll create it via SQL
            logger.info("Tables may need to be created in Supabase dashboard")
            pass

    def _init_sqlite(self):
        """Initialize SQLite database"""
        os.makedirs(
            os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".",
            exist_ok=True,
        )
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()

            # Create users table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create jobs table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    url TEXT UNIQUE,
                    title TEXT,
                    company TEXT,
                    poster TEXT,
                    description TEXT,
                    full_description TEXT,
                    scraped_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """
            )

            # Create cv_generations table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS cv_generations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER,
                    original_cv_content TEXT,
                    tailored_cv_content TEXT,
                    generated_at TIMESTAMP,
                    FOREIGN KEY (job_id) REFERENCES jobs (id)
                )
            """
            )

            # Create linkedin_credentials table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS linkedin_credentials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    encrypted_credentials TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """
            )

            conn.commit()
        finally:
            conn.close()

    def save_job(self, job_data: Dict) -> int:
        """Save job to database"""
        if self.use_supabase:
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
                    self.supabase.table("jobs")
                    .upsert(data, on_conflict="url")
                    .execute()
                )

                if result.data and len(result.data) > 0:
                    return result.data[0]["id"]
                return None
            except Exception as e:
                logger.error(f"Error saving job to Supabase: {e}")
                raise
        else:
            # SQLite implementation
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO jobs (
                        url, title, company, poster, description, full_description, scraped_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        job_data["url"],
                        job_data["title"],
                        job_data["company"],
                        job_data.get("poster"),
                        job_data.get("description"),
                        job_data.get("full_description"),
                        datetime.now().isoformat(),
                    ),
                )

                if cursor.lastrowid:
                    job_id = cursor.lastrowid
                else:
                    cursor.execute(
                        "SELECT id FROM jobs WHERE url = ?", (job_data["url"],)
                    )
                    result = cursor.fetchone()
                    job_id = result[0] if result else None

                conn.commit()
                return job_id
            finally:
                conn.close()

    def check_job_exists(self, url: str) -> Optional[Dict]:
        """Check if job exists by URL"""
        if self.use_supabase:
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
        else:
            # SQLite implementation
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, title, company, scraped_at FROM jobs WHERE url = ?",
                    (url,),
                )
                row = cursor.fetchone()

                if row:
                    return {
                        "id": row[0],
                        "title": row[1],
                        "company": row[2],
                        "scraped_at": str(row[3]),
                    }
                return None
            finally:
                conn.close()

    def get_job(self, job_id: int) -> Optional[Dict]:
        """Get job by ID"""
        if self.use_supabase:
            try:
                result = (
                    self.supabase.table("jobs").select("*").eq("id", job_id).execute()
                )

                if result.data and len(result.data) > 0:
                    return _serialize_datetime(result.data[0])
                return None
            except Exception as e:
                logger.error(f"Error getting job from Supabase: {e}")
                return None
        else:
            # SQLite implementation
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
                row = cursor.fetchone()

                if row:
                    col_names = [desc[0] for desc in cursor.description]
                    return dict(zip(col_names, row))
                return None
            finally:
                conn.close()

    def save_generated_cv(self, job_id: int, original_cv: str, tailored_cv: str):
        """Save generated CV"""
        if self.use_supabase:
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
        else:
            # SQLite implementation
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO cv_generations (
                        job_id, original_cv_content, tailored_cv_content, generated_at
                    ) VALUES (?, ?, ?, ?)
                """,
                    (job_id, original_cv, tailored_cv, datetime.now().isoformat()),
                )
                conn.commit()
            finally:
                conn.close()

    def get_all_jobs(self, limit: int = 10, offset: int = 0) -> List[Dict]:
        """Get all jobs with pagination"""
        if self.use_supabase:
            try:
                result = (
                    self.supabase.table("jobs")
                    .select("id, url, title, company, poster, scraped_at")
                    .order("scraped_at", desc=True)
                    .range(offset, offset + limit - 1)
                    .execute()
                )

                # Serialize datetime objects to strings
                return _serialize_datetime(result.data) if result.data else []
            except Exception as e:
                logger.error(f"Error getting jobs from Supabase: {e}")
                return []
        else:
            # SQLite implementation
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, url, title, company, poster, scraped_at
                    FROM jobs
                    ORDER BY scraped_at DESC
                    LIMIT ? OFFSET ?
                """,
                    (limit, offset),
                )

                rows = cursor.fetchall()

                if cursor.description:
                    col_names = [desc[0] for desc in cursor.description]
                    return [dict(zip(col_names, row)) for row in rows]
                return []
            finally:
                conn.close()

    def delete_job(self, job_id: int) -> bool:
        """Delete job and associated CVs"""
        if self.use_supabase:
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
        else:
            # SQLite implementation
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cv_generations WHERE job_id = ?", (job_id,))
                cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))

                deleted = cursor.rowcount > 0
                conn.commit()
                return deleted
            finally:
                conn.close()

    # User management methods
    def create_user(self, email: str, hashed_password: str) -> int:
        """Create a new user"""
        if self.use_supabase:
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
        else:
            # SQLite implementation
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO users (email, hashed_password)
                    VALUES (?, ?)
                """,
                    (email, hashed_password),
                )
                user_id = cursor.lastrowid
                conn.commit()
                return user_id
            finally:
                conn.close()

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        if self.use_supabase:
            try:
                result = (
                    self.supabase.table("users")
                    .select("*")
                    .eq("email", email)
                    .execute()
                )

                if result.data and len(result.data) > 0:
                    return _serialize_datetime(result.data[0])
                return None
            except Exception as e:
                logger.error(f"Error getting user from Supabase: {e}")
                return None
        else:
            # SQLite implementation
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                row = cursor.fetchone()

                if row:
                    col_names = [desc[0] for desc in cursor.description]
                    return dict(zip(col_names, row))
                return None
            finally:
                conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        if self.use_supabase:
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
        else:
            # SQLite implementation
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                row = cursor.fetchone()

                if row:
                    col_names = [desc[0] for desc in cursor.description]
                    return dict(zip(col_names, row))
                return None
            finally:
                conn.close()

    # LinkedIn credentials management
    def store_linkedin_credentials(self, user_id: int, encrypted_credentials: str):
        """Store encrypted LinkedIn credentials"""
        if self.use_supabase:
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
        else:
            # SQLite implementation
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO linkedin_credentials (user_id, encrypted_credentials, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                    (user_id, encrypted_credentials),
                )
                conn.commit()
            finally:
                conn.close()

    def get_linkedin_credentials(self, user_id: int) -> Optional[str]:
        """Get encrypted LinkedIn credentials"""
        if self.use_supabase:
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
        else:
            # SQLite implementation
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT encrypted_credentials FROM linkedin_credentials WHERE user_id = ?
                """,
                    (user_id,),
                )

                row = cursor.fetchone()
                if row:
                    return row[0]
                return None
            finally:
                conn.close()

    def delete_linkedin_credentials(self, user_id: int) -> bool:
        """Delete LinkedIn credentials"""
        if self.use_supabase:
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
        else:
            # SQLite implementation
            conn = sqlite3.connect(self.db_path)
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM linkedin_credentials WHERE user_id = ?", (user_id,)
                )
                deleted = cursor.rowcount > 0
                conn.commit()
                return deleted
            finally:
                conn.close()
