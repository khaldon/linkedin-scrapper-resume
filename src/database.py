import sqlite3
import json
from datetime import datetime
from typing import Dict, Optional

class Database:
    def __init__(self, db_path: str = "data/jobs.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                company TEXT,
                poster TEXT,
                description TEXT,
                full_description TEXT,
                scraped_at TIMESTAMP
            )
        """)
        
        # Create cv_generations table for tracking generated CVs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cv_generations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                original_cv_content TEXT,
                tailored_cv_content TEXT,
                generated_at TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        """)
        
        conn.commit()
        conn.close()

    def save_job(self, job_data: Dict) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO jobs (
                    url, title, company, poster, description, full_description, scraped_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                job_data['url'],
                job_data['title'],
                job_data['company'],
                job_data['poster'],
                job_data['description'],
                job_data['full_description'],
                datetime.now().isoformat()
            ))
            
            # Get the id of the inserted/updated row
            if cursor.lastrowid:
                job_id = cursor.lastrowid
            else:
                # If it was a replace (update), we need to fetch the ID
                cursor.execute("SELECT id FROM jobs WHERE url = ?", (job_data['url'],))
                job_id = cursor.fetchone()[0]
                
            conn.commit()
            return job_id
        finally:
            conn.close()

    def get_job(self, job_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        conn.row_factory = sqlite3.Row
        
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None

    def save_generated_cv(self, job_id: int, original_cv: str, tailored_cv: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO cv_generations (
                job_id, original_cv_content, tailored_cv_content, generated_at
            ) VALUES (?, ?, ?, ?)
        """, (job_id, original_cv, tailored_cv, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
