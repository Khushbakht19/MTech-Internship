"""
database.py
------------
Handles all interaction with the SQLite database.

Two tables are used:

1. sms_messages
   The labeled training corpus (spam / ham) used to train the
   Naive Bayes classifier.

2. prediction_history
   Every message the user has scanned through the app, together with
   the model's prediction, confidence score, and the suspicious
   keywords that were detected inside it.

3. model_metrics
   Stores the accuracy of the last time the model was trained, so the
   Dashboard can display a "Detection Accuracy" statistic without
   having to retrain the model every time the app opens.

Keeping all SQL in this one class means the GUI code never has to
write a single SQL query directly -- it just calls methods like
`db.get_dashboard_stats()`.
"""

import sqlite3
from datetime import datetime
from collections import Counter

import pandas as pd

import config


class Database:
    """A thin, friendly wrapper around the SQLite database."""

    def __init__(self, db_path=config.DB_PATH):
        self.db_path = db_path
        self.initialize_database()

    # ------------------------------------------------------------------
    # CONNECTION HELPERS
    # ------------------------------------------------------------------
    def get_connection(self):
        """Return a new SQLite connection with row access by column name."""
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def database_exists():
        """Check whether the database file has already been created."""
        return config.DB_PATH.exists()

    # ------------------------------------------------------------------
    # SCHEMA CREATION
    # ------------------------------------------------------------------
    def initialize_database(self):
        """Create every table the app needs if it does not exist yet."""
        connection = self.get_connection()
        cursor = connection.cursor()

        # Training corpus used to teach the Naive Bayes model.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sms_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_text TEXT NOT NULL,
                label TEXT NOT NULL CHECK (label IN ('spam', 'ham')),
                date_added TEXT NOT NULL
            )
        """)

        # Every message the user has scanned through the GUI.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_text TEXT NOT NULL,
                prediction TEXT NOT NULL CHECK (prediction IN ('spam', 'ham')),
                confidence REAL NOT NULL,
                detected_keywords TEXT,
                date_predicted TEXT NOT NULL
            )
        """)

        # Stores the most recent training accuracy of the ML model.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                accuracy REAL NOT NULL,
                trained_on_count INTEGER NOT NULL,
                trained_date TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    # ------------------------------------------------------------------
    # TRAINING DATA (sms_messages)
    # ------------------------------------------------------------------
    def insert_training_message(self, message_text, label):
        """Insert a single labeled message into the training corpus."""
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO sms_messages (message_text, label, date_added) VALUES (?, ?, ?)",
            (message_text.strip(), label, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        connection.commit()
        connection.close()

    def bulk_insert_training_messages(self, messages):
        """
        Insert many (message_text, label) tuples at once.
        Used by seed_data.py to populate the initial dataset quickly.
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rows = [(text.strip(), label, now) for text, label in messages]
        cursor.executemany(
            "INSERT INTO sms_messages (message_text, label, date_added) VALUES (?, ?, ?)",
            rows,
        )
        connection.commit()
        connection.close()

    def get_training_data_count(self):
        """Return how many labeled messages currently exist."""
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) AS count FROM sms_messages")
        count = cursor.fetchone()["count"]
        connection.close()
        return count

    def get_training_dataframe(self):
        """Return the entire training corpus as a pandas DataFrame."""
        connection = self.get_connection()
        dataframe = pd.read_sql_query(
            "SELECT message_text, label FROM sms_messages", connection
        )
        connection.close()
        return dataframe

    # ------------------------------------------------------------------
    # PREDICTION HISTORY
    # ------------------------------------------------------------------
    def insert_prediction(self, message_text, prediction, confidence, detected_keywords):
        """
        Save a single prediction made by the Scanner page.

        detected_keywords is expected to be a comma-separated string
        (e.g. "free, winner, claim") or an empty string if none found.
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO prediction_history
               (message_text, prediction, confidence, detected_keywords, date_predicted)
               VALUES (?, ?, ?, ?, ?)""",
            (
                message_text.strip(),
                prediction,
                round(float(confidence), 2),
                detected_keywords,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        connection.commit()
        new_id = cursor.lastrowid
        connection.close()
        return new_id

    def get_all_predictions(self, limit=None):
        """Return every prediction, most recent first."""
        connection = self.get_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM prediction_history ORDER BY id DESC"
        if limit:
            query += f" LIMIT {int(limit)}"
        cursor.execute(query)
        rows = [dict(row) for row in cursor.fetchall()]
        connection.close()
        return rows

    def get_recent_predictions(self, limit=5):
        """Convenience wrapper used by the Dashboard's 'Recent Predictions' card."""
        return self.get_all_predictions(limit=limit)

    def search_predictions(self, keyword):
        """Search prediction history by message text (used by the search bar)."""
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """SELECT * FROM prediction_history
               WHERE message_text LIKE ?
               ORDER BY id DESC""",
            (f"%{keyword}%",),
        )
        rows = [dict(row) for row in cursor.fetchall()]
        connection.close()
        return rows

    def filter_predictions(self, prediction_label):
        """Filter prediction history by 'spam' or 'ham'."""
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM prediction_history WHERE prediction = ? ORDER BY id DESC",
            (prediction_label,),
        )
        rows = [dict(row) for row in cursor.fetchall()]
        connection.close()
        return rows

    def clear_prediction_history(self):
        """Delete every row from prediction_history (used by a 'Clear History' action)."""
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM prediction_history")
        connection.commit()
        connection.close()

    # ------------------------------------------------------------------
    # MODEL METRICS
    # ------------------------------------------------------------------
    def save_model_metrics(self, accuracy, trained_on_count):
        """Store the accuracy achieved the last time the model was trained."""
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """INSERT INTO model_metrics (accuracy, trained_on_count, trained_date)
               VALUES (?, ?, ?)""",
            (round(float(accuracy), 4), trained_on_count,
             datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        connection.commit()
        connection.close()

    def get_latest_model_metrics(self):
        """Return the most recent accuracy record, or None if never trained."""
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM model_metrics ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        connection.close()
        return dict(row) if row else None

    # ------------------------------------------------------------------
    # DASHBOARD / ANALYTICS AGGREGATES
    # ------------------------------------------------------------------
    def get_dashboard_stats(self):
        """
        Return the four headline numbers shown on the Dashboard:
        total scanned, spam count, safe count, and detection accuracy.
        """
        connection = self.get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) AS count FROM prediction_history")
        total = cursor.fetchone()["count"]

        cursor.execute(
            "SELECT COUNT(*) AS count FROM prediction_history WHERE prediction = 'spam'"
        )
        spam_count = cursor.fetchone()["count"]

        cursor.execute(
            "SELECT COUNT(*) AS count FROM prediction_history WHERE prediction = 'ham'"
        )
        safe_count = cursor.fetchone()["count"]

        connection.close()

        metrics = self.get_latest_model_metrics()
        accuracy = metrics["accuracy"] * 100 if metrics else 0.0

        return {
            "total": total,
            "spam_count": spam_count,
            "safe_count": safe_count,
            "accuracy": round(accuracy, 1),
        }

    def get_top_threat_keyword(self):
        """
        Look through every spam prediction's detected_keywords column and
        return the single most frequently seen suspicious keyword.
        Used by the Dashboard's 'Top Detected Threat' card.
        """
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT detected_keywords FROM prediction_history WHERE prediction = 'spam'"
        )
        rows = cursor.fetchall()
        connection.close()

        keyword_counter = Counter()
        for row in rows:
            keywords_string = row["detected_keywords"] or ""
            for keyword in keywords_string.split(","):
                keyword = keyword.strip()
                if keyword:
                    keyword_counter[keyword] += 1

        if not keyword_counter:
            return "N/A"

        top_keyword, _ = keyword_counter.most_common(1)[0]
        return top_keyword

    def get_spam_distribution(self):
        """Return (spam_count, ham_count) for pie/bar charts on Dashboard/Analytics."""
        stats = self.get_dashboard_stats()
        return stats["spam_count"], stats["safe_count"]
