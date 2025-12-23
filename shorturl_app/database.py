"""
Подключение к базе данных SQLite для сервиса сокращения URL
"""

import sqlite3
import os
import string
import random

# Путь к базе данных
DB_PATH = "/app/data/shorturl.db"

def get_db_connection():
    """Создает соединение с базой данных"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_short_id(length=6):
    """Генерирует короткий ID для ссылки"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def init_db():
    """Инициализирует базу данных для URL Shortener"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_id TEXT UNIQUE NOT NULL,
        original_url TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        click_count INTEGER DEFAULT 0
    )
    ''')

    # Создаем индекс для быстрого поиска по short_id
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_short_id ON urls(short_id)
    ''')

    conn.commit()
    conn.close()
    print("✅ База данных URL Shortener инициализирована")

if __name__ == "__main__":
    init_db()