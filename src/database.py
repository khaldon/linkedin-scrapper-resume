import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Optional


class Database:
    def __init__(self, db_path: Optional[str] = None):
        # Set default db_path always
        if db_path is None:
            self.db_path = os.getenv("DATABASE_PATH", "data/jobs.db")
        else:
            self.db_path = db_path

        # Check for Turso configuration
        self.turso_url = os.getenv("TURSO_DATABASE_URL")
        self.turso_token = os.getenv("TURSO_AUTH_TOKEN")
        self.use_turso = bool(self.turso_url and self.turso_token)

        # Verify Turso connection immediately if enabled
        if self.use_turso:
            print(f"🚀 Testing Turso Connection: {self.turso_url}")
            try:
                import libsql_experimental as libsql

                # Try to connect and run a simple query to ensure it actually works
                # We use a fresh connection here just for testing
                conn = libsql.connect(self.turso_url, auth_token=self.turso_token)
                conn.execute("SELECT 1")
                if hasattr(conn, "close"):
                    conn.close()
                print("✅ Turso Connection Verified!")
            except BaseException as e:
                # Catch ALL errors including Panics (BaseException)
                print(f"⚠️ Turso connection FAILED: {e}")
                print("⚠️ Disabling Turso and falling back to local SQLite.")
                self.use_turso = False

        if self.use_turso:
            print(f"🚀 Using Turso Database: {self.turso_url}")
        else:
            print(f"📂 Using Local SQLite: {self.db_path}")

        self._init_db()

    def _get_connection(self):
        """Get a database connection (Local SQLite or Remote Turso)"""
        if self.use_turso:
            try:
                import libsql_experimental as libsql

                return libsql.connect(self.turso_url, auth_token=self.turso_token)
            except BaseException as e:
                print(f"⚠️ Turso connection failed: {e}. Falling back to local SQLite.")
                self.use_turso = False
                return sqlite3.connect(self.db_path)
        else:
            return sqlite3.connect(self.db_path)

    def _close_connection(self, conn):
        """Safely close database connection"""
        try:
            if hasattr(conn, "close"):
                conn.close()
        except BaseException:
            pass

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create users table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
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

        # Create cv_generations table for tracking generated CVs
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

        # Create linkedin_credentials table for encrypted credentials
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
        self._close_connection(conn)

    def save_job(self, job_data: Dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
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
                    job_data["poster"],
                    job_data["description"],
                    job_data["full_description"],
                    datetime.now().isoformat(),
                ),
            )

            # Get the id of the inserted/updated row
            if cursor.lastrowid:
                job_id = cursor.lastrowid
            else:
                # If it was a replace (update), we need to fetch the ID
                cursor.execute("SELECT id FROM jobs WHERE url = ?", (job_data["url"],))
                result = cursor.fetchone()
                # Handle difference between sqlite3 (tuple) and libsql (sometimes object)
                job_id = result[0] if result else None

            conn.commit()
            return job_id
        finally:
            self._close_connection(conn)

    def check_job_exists(self, url: str) -> Optional[Dict]:
        """Check if a job with this URL already exists"""
        conn = self._get_connection()
        # Note: libsql might not support row_factory assignment the same way
        # We'll handle row conversion manually to be safe across both
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, title, company, scraped_at FROM jobs WHERE url = ?", (url,)
        )
        row = cursor.fetchone()
        self._close_connection(conn)

        if row:
            # Convert tuple/row to dict manually
            return {
                "id": row[0],
                "title": row[1],
                "company": row[2],
                "scraped_at": row[3],
            }
        return None

    def get_job(self, job_id: int) -> Optional[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()

        # Get column names to create dict
        if row:
            col_names = [description[0] for description in cursor.description]
            result = dict(zip(col_names, row))
            self._close_connection(conn)
            return result

        self._close_connection(conn)
        return None

    def save_generated_cv(self, job_id: int, original_cv: str, tailored_cv: str):
        conn = self._get_connection()
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
        self._close_connection(conn)

    def get_all_jobs(self, limit: int = 10, offset: int = 0):
        """Get all jobs with pagination"""
        conn = self._get_connection()
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

        # Get column names
        if cursor.description:
            col_names = [description[0] for description in cursor.description]
            results = [dict(zip(col_names, row)) for row in rows]
        else:
            results = []

        self._close_connection(conn)
        return results

    def delete_job(self, job_id: int) -> bool:
        """Delete a job and its associated CV generations"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # Delete associated CV generations first
            cursor.execute("DELETE FROM cv_generations WHERE job_id = ?", (job_id,))

            # Delete the job
            cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))

            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            self._close_connection(conn)

    # User management methods
    def create_user(self, email: str, hashed_password: str) -> int:
        """Create a new user"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
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
            self._close_connection(conn)

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()

        if row:
            col_names = [description[0] for description in cursor.description]
            result = dict(zip(col_names, row))
            self._close_connection(conn)
            return result

        self._close_connection(conn)
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()

        if row:
            col_names = [description[0] for description in cursor.description]
            result = dict(zip(col_names, row))
            self._close_connection(conn)
            return result

        self._close_connection(conn)
        return None

    # LinkedIn credentials management
    def store_linkedin_credentials(self, user_id: int, encrypted_credentials: str):
        """Store encrypted LinkedIn credentials for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
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
        """Get encrypted LinkedIn credentials for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT encrypted_credentials FROM linkedin_credentials WHERE user_id = ?
        """,
            (user_id,),
        )

        row = cursor.fetchone()
        self._close_connection(conn)

        if row:
            return row[0]
        return None

    def delete_linkedin_credentials(self, user_id: int) -> bool:
        """Delete LinkedIn credentials for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM linkedin_credentials WHERE user_id = ?", (user_id,)
            )
            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            self._close_connection(conn)
