"""
Подключение к базе данных SQLite для ToDo приложения
Создаем таблицу tasks при запуске
"""

import sqlite3
import os

# Путь к базе данных - будет в томе Docker
DB_PATH = "/app/data/todo.db"

def get_db_connection():
    """Создает соединение с базой данных"""
    # Создаем директорию, если её нет
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Чтобы возвращать словари
    return conn

def init_db():
    """Инициализирует базу данных, создает таблицу если её нет"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Создаем таблицу tasks
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        completed BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ База данных ToDo инициализирована")

if __name__ == "__main__":
    # При прямом запуске файла инициализируем БД
    init_db()