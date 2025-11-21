import sqlite3
import os
import logging
from datetime import datetime
from typing import Dict, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import psycopg2

    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False


class Database:
    def __init__(self, db_path: Optional[str] = None):
        # Check for Supabase/Postgres configuration
        self.db_url = os.getenv("SUPABASE_DATABASE_URL") or os.getenv("DATABASE_URL")
        self.use_postgres = bool(self.db_url and HAS_POSTGRES)

        # Set SQLite path as fallback
        if db_path is None:
            self.db_path = os.getenv("DATABASE_PATH", "data/jobs.db")
        else:
            self.db_path = db_path

        if self.use_postgres:
            logger.info("🚀 Attempting to use Supabase/PostgreSQL Database")
            # Try to connect to PostgreSQL, fall back to SQLite if it fails
            try:
                self._init_db()
                logger.info("✅ Successfully connected to PostgreSQL")
            except Exception as e:
                logger.error(f"❌ PostgreSQL connection failed: {e}")
                logger.warning(f"⚠️  Falling back to SQLite: {self.db_path}")
                self.use_postgres = False
                self._init_db()
        else:
            logger.info(f"📂 Using Local SQLite: {self.db_path}")
            self._init_db()

    def _get_connection(self):
        """Get a database connection (Local SQLite or Remote Postgres)"""
        if self.use_postgres:
            try:
                # Add connection timeout to prevent hanging
                return psycopg2.connect(
                    self.db_url,
                    connect_timeout=10,  # 10 second timeout
                    options="-c statement_timeout=30000",  # 30 second query timeout
                )
            except Exception as e:
                logger.error(f"❌ Postgres connection failed: {e}")
                raise
        else:
            return sqlite3.connect(self.db_path)

    def _close_connection(self, conn):
        """Safely close database connection"""
        try:
            if hasattr(conn, "close"):
                conn.close()
        except Exception:
            pass

    def _execute(self, cursor, query: str, params: tuple = ()):
        """Execute query with parameter substitution based on DB type"""
        if self.use_postgres:
            # Convert ? to %s for Postgres
            query = query.replace("?", "%s")
            cursor.execute(query, params)
        else:
            cursor.execute(query, params)

    def _init_db(self):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Define types for different DBs
            if self.use_postgres:
                id_type = "SERIAL PRIMARY KEY"
                timestamp_default = "DEFAULT CURRENT_TIMESTAMP"
                bool_type = "BOOLEAN"
            else:
                id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"
                timestamp_default = "DEFAULT CURRENT_TIMESTAMP"
                bool_type = "BOOLEAN"  # SQLite accepts BOOLEAN (as integer)

            # Create users table
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS users (
                    id {id_type},
                    email TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    is_active {bool_type} DEFAULT TRUE,
                    created_at TIMESTAMP {timestamp_default}
                )
            """
            )

            # Create jobs table
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS jobs (
                    id {id_type},
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
                f"""
                CREATE TABLE IF NOT EXISTS cv_generations (
                    id {id_type},
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
                f"""
                CREATE TABLE IF NOT EXISTS linkedin_credentials (
                    id {id_type},
                    user_id INTEGER UNIQUE,
                    encrypted_credentials TEXT NOT NULL,
                    updated_at TIMESTAMP {timestamp_default},
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """
            )

            conn.commit()
        finally:
            self._close_connection(conn)

    def save_job(self, job_data: Dict) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            if self.use_postgres:
                # Postgres UPSERT
                query = """
                    INSERT INTO jobs (
                        url, title, company, poster, description, full_description, scraped_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE SET
                        title = EXCLUDED.title,
                        company = EXCLUDED.company,
                        poster = EXCLUDED.poster,
                        description = EXCLUDED.description,
                        full_description = EXCLUDED.full_description,
                        scraped_at = EXCLUDED.scraped_at
                    RETURNING id
                """
                cursor.execute(
                    query,
                    (
                        job_data["url"],
                        job_data["title"],
                        job_data["company"],
                        job_data["poster"],
                        job_data["description"],
                        job_data["full_description"],
                        datetime.now().isoformat(),
                    ),
                )
                job_id = cursor.fetchone()[0]
            else:
                # SQLite UPSERT (INSERT OR REPLACE)
                self._execute(
                    cursor,
                    """
                    INSERT OR REPLACE INTO jobs (
                        url, title, company, poster, description, full_description, scraped_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        job_data["url"],
                        job_data["title"],
                        job_data["company"],
                        job_data["poster"],
                        job_data["description"],
                        job_data["full_description"],
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
            self._close_connection(conn)

    def check_job_exists(self, url: str) -> Optional[Dict]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            self._execute(
                cursor,
                "SELECT id, title, company, scraped_at FROM jobs WHERE url = ?",
                (url,),
            )
            row = cursor.fetchone()

            if row:
                # Handle tuple vs RealDictRow if we used RealDictCursor (but we didn't here for consistency)
                return {
                    "id": row[0],
                    "title": row[1],
                    "company": row[2],
                    "scraped_at": str(row[3]),  # Ensure string for timestamp
                }
            return None
        finally:
            self._close_connection(conn)

    def get_job(self, job_id: int) -> Optional[Dict]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            self._execute(cursor, "SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()

            if row:
                col_names = [desc[0] for desc in cursor.description]
                return dict(zip(col_names, row))
            return None
        finally:
            self._close_connection(conn)

    def save_generated_cv(self, job_id: int, original_cv: str, tailored_cv: str):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            self._execute(
                cursor,
                """
                INSERT INTO cv_generations (
                    job_id, original_cv_content, tailored_cv_content, generated_at
                ) VALUES (?, ?, ?, ?)
            """,
                (job_id, original_cv, tailored_cv, datetime.now().isoformat()),
            )
            conn.commit()
        finally:
            self._close_connection(conn)

    def get_all_jobs(self, limit: int = 10, offset: int = 0):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            self._execute(
                cursor,
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
            self._close_connection(conn)

    def delete_job(self, job_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            self._execute(
                cursor, "DELETE FROM cv_generations WHERE job_id = ?", (job_id,)
            )
            self._execute(cursor, "DELETE FROM jobs WHERE id = ?", (job_id,))

            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            self._close_connection(conn)

    # User management methods
    def create_user(self, email: str, hashed_password: str) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            if self.use_postgres:
                cursor.execute(
                    """
                    INSERT INTO users (email, hashed_password)
                    VALUES (%s, %s)
                    RETURNING id
                """,
                    (email, hashed_password),
                )
                user_id = cursor.fetchone()[0]
            else:
                self._execute(
                    cursor,
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
            self._close_connection(conn)

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            self._execute(cursor, "SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()

            if row:
                col_names = [desc[0] for desc in cursor.description]
                return dict(zip(col_names, row))
            return None
        finally:
            self._close_connection(conn)

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            self._execute(cursor, "SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()

            if row:
                col_names = [desc[0] for desc in cursor.description]
                return dict(zip(col_names, row))
            return None
        finally:
            self._close_connection(conn)

    # LinkedIn credentials management
    def store_linkedin_credentials(self, user_id: int, encrypted_credentials: str):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            if self.use_postgres:
                query = """
                    INSERT INTO linkedin_credentials (user_id, encrypted_credentials, updated_at)
                    VALUES (%s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id) DO UPDATE SET
                        encrypted_credentials = EXCLUDED.encrypted_credentials,
                        updated_at = CURRENT_TIMESTAMP
                """
                cursor.execute(query, (user_id, encrypted_credentials))
            else:
                self._execute(
                    cursor,
                    """
                    INSERT OR REPLACE INTO linkedin_credentials (user_id, encrypted_credentials, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                    (user_id, encrypted_credentials),
                )

            conn.commit()
        finally:
            self._close_connection(conn)

    def get_linkedin_credentials(self, user_id: int) -> Optional[str]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            self._execute(
                cursor,
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
            self._close_connection(conn)

    def delete_linkedin_credentials(self, user_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            self._execute(
                cursor, "DELETE FROM linkedin_credentials WHERE user_id = ?", (user_id,)
            )
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            self._close_connection(conn)
