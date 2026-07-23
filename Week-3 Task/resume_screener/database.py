"""
database.py
------------------------------------------------------------------
Handles all SQLite database operations for Resume Screener Pro.

Responsibilities:
    - Create the database schema (Candidates, Jobs, Screening History)
    - Automatically seed sample data on first run
    - Provide clean CRUD methods used by the GUI layer
    - Provide aggregate queries used by the Dashboard and Analytics pages

The GUI code never writes raw SQL directly - it always goes through
the DatabaseManager class below. This keeps the project modular and
easy to maintain.
------------------------------------------------------------------
"""

import os
import sqlite3
from datetime import datetime

import config


# ==================================================================
# DATABASE SCHEMA
# ==================================================================
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS candidates (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name       TEXT NOT NULL,
    email           TEXT,
    phone           TEXT,
    skills          TEXT,              -- comma separated skill list
    experience_years REAL DEFAULT 0,
    education       TEXT,
    resume_text     TEXT NOT NULL,     -- cleaned resume content used for NLP
    file_name       TEXT,              -- original uploaded file name (if any)
    date_added      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title           TEXT NOT NULL,
    department          TEXT,
    required_skills     TEXT,          -- comma separated required skills
    experience_required REAL DEFAULT 0,
    job_description     TEXT NOT NULL,
    date_posted         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS screening_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id    INTEGER NOT NULL,
    job_id          INTEGER NOT NULL,
    match_score     REAL NOT NULL,
    matched_keywords TEXT,
    rank_position   INTEGER,
    screening_date  TEXT NOT NULL,
    FOREIGN KEY (candidate_id) REFERENCES candidates (id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_screening_job ON screening_history (job_id);
CREATE INDEX IF NOT EXISTS idx_screening_candidate ON screening_history (candidate_id);
"""


class DatabaseManager:
    """
    Provides a simple, safe interface over the SQLite database used
    by the whole application. One instance is created in main.py and
    passed down to every GUI page that needs data.
    """

    def __init__(self, db_path=config.DB_PATH):
        self.db_path = db_path

    # --------------------------------------------------------------
    # CONNECTION HELPERS
    # --------------------------------------------------------------
    def get_connection(self):
        """Open a new SQLite connection with row access by column name."""
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    @staticmethod
    def _row_to_dict(row):
        """Convert a sqlite3.Row into a plain Python dictionary."""
        return dict(row) if row is not None else None

    @staticmethod
    def _rows_to_list(rows):
        """Convert a list of sqlite3.Row objects into a list of dicts."""
        return [dict(row) for row in rows]

    # --------------------------------------------------------------
    # INITIALIZATION
    # --------------------------------------------------------------
    def initialize_database(self):
        """
        Creates the database schema if it does not already exist and
        loads realistic sample data the very first time the app runs.
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.executescript(SCHEMA_SQL)
        connection.commit()

        cursor.execute("SELECT COUNT(*) FROM candidates")
        candidate_count = cursor.fetchone()[0]
        connection.close()

        # Only seed the database if it is completely empty.
        if candidate_count == 0:
            from seed_data import seed_database
            seed_database(self.db_path)

    # ================================================================
    # CANDIDATES
    # ================================================================
    def add_candidate(self, full_name, email, phone, skills,
                       experience_years, education, resume_text, file_name=None):
        """Insert a new candidate record and return its new ID."""
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO candidates
                (full_name, email, phone, skills, experience_years,
                 education, resume_text, file_name, date_added)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (full_name, email, phone, skills, experience_years,
             education, resume_text, file_name,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        connection.commit()
        new_id = cursor.lastrowid
        connection.close()
        return new_id

    def get_all_candidates(self, search_term=None):
        """
        Return all candidates, optionally filtered by a search term
        matching name or skills (used by the Candidates page search box).
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        if search_term:
            like_pattern = f"%{search_term}%"
            cursor.execute(
                """
                SELECT * FROM candidates
                WHERE full_name LIKE ? OR skills LIKE ? OR education LIKE ?
                ORDER BY date_added DESC
                """,
                (like_pattern, like_pattern, like_pattern)
            )
        else:
            cursor.execute("SELECT * FROM candidates ORDER BY date_added DESC")
        rows = cursor.fetchall()
        connection.close()
        return self._rows_to_list(rows)

    def get_candidate_by_id(self, candidate_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
        row = cursor.fetchone()
        connection.close()
        return self._row_to_dict(row)

    def update_candidate(self, candidate_id, full_name, email, phone, skills,
                          experience_years, education, resume_text):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE candidates
            SET full_name = ?, email = ?, phone = ?, skills = ?,
                experience_years = ?, education = ?, resume_text = ?
            WHERE id = ?
            """,
            (full_name, email, phone, skills, experience_years,
             education, resume_text, candidate_id)
        )
        connection.commit()
        connection.close()

    def delete_candidate(self, candidate_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
        connection.commit()
        connection.close()

    def get_candidates_count(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM candidates")
        count = cursor.fetchone()[0]
        connection.close()
        return count

    # ================================================================
    # JOBS
    # ================================================================
    def add_job(self, job_title, department, required_skills,
                experience_required, job_description):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO jobs
                (job_title, department, required_skills,
                 experience_required, job_description, date_posted)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (job_title, department, required_skills, experience_required,
             job_description, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        connection.commit()
        new_id = cursor.lastrowid
        connection.close()
        return new_id

    def get_all_jobs(self, search_term=None):
        connection = self.get_connection()
        cursor = connection.cursor()
        if search_term:
            like_pattern = f"%{search_term}%"
            cursor.execute(
                """
                SELECT * FROM jobs
                WHERE job_title LIKE ? OR department LIKE ? OR required_skills LIKE ?
                ORDER BY date_posted DESC
                """,
                (like_pattern, like_pattern, like_pattern)
            )
        else:
            cursor.execute("SELECT * FROM jobs ORDER BY date_posted DESC")
        rows = cursor.fetchall()
        connection.close()
        return self._rows_to_list(rows)

    def get_job_by_id(self, job_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        connection.close()
        return self._row_to_dict(row)

    def update_job(self, job_id, job_title, department, required_skills,
                   experience_required, job_description):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE jobs
            SET job_title = ?, department = ?, required_skills = ?,
                experience_required = ?, job_description = ?
            WHERE id = ?
            """,
            (job_title, department, required_skills,
             experience_required, job_description, job_id)
        )
        connection.commit()
        connection.close()

    def delete_job(self, job_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        connection.commit()
        connection.close()

    def get_jobs_count(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM jobs")
        count = cursor.fetchone()[0]
        connection.close()
        return count

    # ================================================================
    # SCREENING HISTORY
    # ================================================================
    def add_screening_record(self, candidate_id, job_id, match_score,
                              matched_keywords, rank_position=None):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO screening_history
                (candidate_id, job_id, match_score, matched_keywords,
                 rank_position, screening_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (candidate_id, job_id, match_score, matched_keywords,
             rank_position, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        connection.commit()
        new_id = cursor.lastrowid
        connection.close()
        return new_id

    def get_all_screenings(self, job_id=None, min_score=None, search_term=None):
        """
        Return screening history joined with candidate & job names.
        Supports optional filtering used by the History page.
        """
        connection = self.get_connection()
        cursor = connection.cursor()

        query = """
            SELECT sh.id, sh.match_score, sh.matched_keywords,
                   sh.rank_position, sh.screening_date,
                   c.id AS candidate_id, c.full_name AS candidate_name,
                   j.id AS job_id, j.job_title AS job_title
            FROM screening_history sh
            JOIN candidates c ON sh.candidate_id = c.id
            JOIN jobs j ON sh.job_id = j.id
            WHERE 1 = 1
        """
        params = []

        if job_id:
            query += " AND sh.job_id = ?"
            params.append(job_id)
        if min_score is not None:
            query += " AND sh.match_score >= ?"
            params.append(min_score)
        if search_term:
            query += " AND (c.full_name LIKE ? OR j.job_title LIKE ?)"
            like_pattern = f"%{search_term}%"
            params.extend([like_pattern, like_pattern])

        query += " ORDER BY sh.screening_date DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        connection.close()
        return self._rows_to_list(rows)

    def get_recent_screenings(self, limit=5):
        """Used by the Dashboard's 'Recent Screenings' widget."""
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT sh.match_score, sh.screening_date,
                   c.full_name AS candidate_name,
                   j.job_title AS job_title
            FROM screening_history sh
            JOIN candidates c ON sh.candidate_id = c.id
            JOIN jobs j ON sh.job_id = j.id
            ORDER BY sh.screening_date DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        connection.close()
        return self._rows_to_list(rows)

    def get_rankings_for_job(self, job_id):
        """
        Return every candidate screened against a given job,
        ordered from highest to lowest match score (ranking).
        Used by the Screening page to display ranked results.
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT sh.match_score, sh.matched_keywords, sh.screening_date,
                   c.id AS candidate_id, c.full_name, c.email,
                   c.skills, c.experience_years
            FROM screening_history sh
            JOIN candidates c ON sh.candidate_id = c.id
            WHERE sh.job_id = ?
            ORDER BY sh.match_score DESC
            """,
            (job_id,)
        )
        rows = cursor.fetchall()
        connection.close()
        return self._rows_to_list(rows)

    def delete_screening_record(self, screening_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM screening_history WHERE id = ?", (screening_id,))
        connection.commit()
        connection.close()

    def get_screenings_count(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM screening_history")
        count = cursor.fetchone()[0]
        connection.close()
        return count

    # ================================================================
    # DASHBOARD & ANALYTICS AGGREGATE QUERIES
    # ================================================================
    def get_dashboard_stats(self):
        """
        Returns a dictionary with the four headline dashboard metrics:
        total candidates, total jobs, total screening sessions,
        and the average match score across all screenings.
        """
        connection = self.get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM candidates")
        total_candidates = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM jobs")
        total_jobs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM screening_history")
        total_screenings = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(match_score) FROM screening_history")
        avg_score = cursor.fetchone()[0]

        connection.close()

        return {
            "total_candidates": total_candidates,
            "total_jobs": total_jobs,
            "total_screenings": total_screenings,
            "average_match_score": round(avg_score, 1) if avg_score else 0.0,
        }

    def get_top_candidate(self):
        """
        Returns the candidate with the single highest match score
        recorded anywhere in the screening history (for the
        Dashboard's 'Top Candidate' card).
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT c.full_name, c.email, c.skills,
                   sh.match_score, j.job_title
            FROM screening_history sh
            JOIN candidates c ON sh.candidate_id = c.id
            JOIN jobs j ON sh.job_id = j.id
            ORDER BY sh.match_score DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        connection.close()
        return self._row_to_dict(row)

    def get_top_candidates_overall(self, limit=8):
        """
        Returns the top N distinct candidates by their best match
        score. Used to draw the Dashboard's ranking bar chart.
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT c.full_name, MAX(sh.match_score) AS best_score
            FROM screening_history sh
            JOIN candidates c ON sh.candidate_id = c.id
            GROUP BY c.id
            ORDER BY best_score DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = cursor.fetchall()
        connection.close()
        return self._rows_to_list(rows)

    def get_score_distribution(self):
        """
        Returns counts of screenings grouped into score bands
        (Excellent / Good / Average / Low). Used by the Analytics page.
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT match_score FROM screening_history")
        scores = [row[0] for row in cursor.fetchall()]
        connection.close()

        distribution = {"Excellent": 0, "Good": 0, "Average": 0, "Low": 0}
        for score in scores:
            if score >= config.SCORE_THRESHOLDS["excellent"]:
                distribution["Excellent"] += 1
            elif score >= config.SCORE_THRESHOLDS["good"]:
                distribution["Good"] += 1
            elif score >= config.SCORE_THRESHOLDS["average"]:
                distribution["Average"] += 1
            else:
                distribution["Low"] += 1
        return distribution

    def get_screenings_per_job(self):
        """Returns the number of screenings recorded for each job title."""
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT j.job_title, COUNT(sh.id) AS screening_count,
                   AVG(sh.match_score) AS avg_score
            FROM jobs j
            LEFT JOIN screening_history sh ON j.id = sh.job_id
            GROUP BY j.id
            ORDER BY screening_count DESC
            """
        )
        rows = cursor.fetchall()
        connection.close()
        return self._rows_to_list(rows)
