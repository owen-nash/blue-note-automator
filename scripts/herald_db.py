import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "herald.db")

def init_db():
    """Initializes the database and creates the articles table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            published_date TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def is_article_processed(link):
    """Checks if an article has already been processed based on its link."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM articles WHERE link = ?', (link,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def mark_article_processed(source, title, link, published_date=None):
    """Saves a new article link to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO articles (source, title, link, published_date)
            VALUES (?, ?, ?, ?)
        ''', (source, title, link, published_date))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def prune_old_articles(days=30):
    """Deletes records older than the specified number of days."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('DELETE FROM articles WHERE processed_at < ?', (cutoff_date,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    if deleted_count > 0:
        print(f"Pruned {deleted_count} old article records from Herald DB.")
    return deleted_count

if __name__ == "__main__":
    init_db()
    print("Herald Database initialized.")
    # Quick test
    mark_article_processed("Test Source", "Test Title", "http://example.com/1")
    print(f"Article processed check: {is_article_processed('http://example.com/1')}")
    prune_old_articles()
