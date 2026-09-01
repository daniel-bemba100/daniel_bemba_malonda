"""SQLite Database manager for application data and settings."""

import sqlite3
import logging
from pathlib import Path
from typing import Any, List, Dict, Optional

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages SQLite database for settings and snippets."""

    def __init__(self, db_path: Path | str | None = None):
        if db_path is None:
            db_path = Path(__file__).resolve().parent.parent.parent / "app_data.db"
        self._path = Path(db_path)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a configured SQLite connection."""
        conn = sqlite3.connect(str(self._path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initialize the database schema if it doesn't exist."""
        try:
            with self._get_connection() as conn:
                # Settings table (key-value store)
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL
                    )
                ''')
                # Snippets table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS snippets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        language TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logger.info("Database initialized at %s", self._path)
        except sqlite3.Error as e:
            logger.error("Failed to initialize database: %s", e)

    # --- Settings API ---

    def get_setting(self, key: str, default: Any = None) -> Any:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    import json
                    return json.loads(row['value'])
        except Exception as e:
            logger.error("Error reading setting %s: %s", key, e)
        return default

    def set_setting(self, key: str, value: Any) -> None:
        try:
            import json
            value_str = json.dumps(value)
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, value_str)
                )
                conn.commit()
        except Exception as e:
            logger.error("Error saving setting %s: %s", key, e)

    # --- Snippets API ---

    def add_snippet(self, title: str, content: str, language: str = "plain") -> int:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO snippets (title, content, language) VALUES (?, ?, ?)",
                    (title, content, language)
                )
                conn.commit()
                return cursor.lastrowid or -1
        except Exception as e:
            logger.error("Error adding snippet: %s", e)
            return -1

    def get_all_snippets(self) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT * FROM snippets ORDER BY created_at DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error("Error getting snippets: %s", e)
            return []

    def delete_snippet(self, snippet_id: int) -> bool:
        try:
            with self._get_connection() as conn:
                conn.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error("Error deleting snippet: %s", e)
            return False
