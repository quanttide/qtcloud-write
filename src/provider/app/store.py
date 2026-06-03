import json
import sqlite3
from pathlib import Path
from app.config import get_settings
from app.models import Article


class StyleStore:
    """SQLite-backed style accumulation."""

    def __init__(self):
        settings = get_settings()
        Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
        self._db_path = Path(settings.data_dir) / "store.db"
        self._init_db()

    def _conn(self):
        return sqlite3.connect(str(self._db_path))

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS good_articles (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    paragraphs TEXT NOT NULL,
                    author TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)

    def add_good(self, article: Article):
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO good_articles (id, title, paragraphs, author, tag) VALUES (?, ?, ?, ?, ?)",
                (article.id, article.title, json.dumps(article.paragraphs, ensure_ascii=False), article.author, article.tag),
            )

    @property
    def is_available(self) -> bool:
        with self._conn() as conn:
            row = conn.execute("SELECT COUNT(*) FROM good_articles").fetchone()
            return row[0] > 0 if row else False

    @property
    def good_articles(self) -> list[Article]:
        with self._conn() as conn:
            rows = conn.execute("SELECT id, title, paragraphs, author, tag FROM good_articles ORDER BY created_at").fetchall()
            result = []
            for row in rows:
                result.append(Article(
                    id=row[0],
                    title=row[1],
                    paragraphs=json.loads(row[2]),
                    author=row[3],
                    tag=row[4],
                ))
            return result

    @property
    def count(self) -> int:
        with self._conn() as conn:
            row = conn.execute("SELECT COUNT(*) FROM good_articles").fetchone()
            return row[0] if row else 0

    def clear(self):
        with self._conn() as conn:
            conn.execute("DELETE FROM good_articles")


style_store = StyleStore()
