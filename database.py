"""
database.py - Simple Database
"""

import sqlite3
import logging
from config import DATABASE_FILE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            source TEXT,
            published_date TEXT,
            summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

def save_news(title, link, source, published_date="", summary=""):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO news (title, link, source, published_date, summary)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, link, source, published_date, summary))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error saving: {e}")
        return False

def get_all_saved_links():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT link FROM news")
    links = cursor.fetchall()
    conn.close()
    return {link[0] for link in links}

def get_all_news(limit=20):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, link, source, published_date, summary, created_at
        FROM news ORDER BY created_at DESC LIMIT ?
    ''', (limit,))
    news = cursor.fetchall()
    conn.close()
    return news