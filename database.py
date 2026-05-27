import aiosqlite
from pathlib import Path
import os
from typing import Optional

DATABASE_PATH = os.getenv("DATABASE_PATH", "data/database.db")
DB_PATH = Path(DATABASE_PATH)


async def init_db() -> None:
    """Инициализация всех таблиц и загрузка фраз из файла, если они еще не загружены."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(DB_PATH)) as db:
        # Таблица users
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                display_name TEXT DEFAULT '',
                verified INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Добавляем колонку display_name, если её нет (миграция)
        async with db.execute("PRAGMA table_info(users)") as cur:
            columns = [row[1] for row in await cur.fetchall()]
            if 'display_name' not in columns:
                await db.execute("ALTER TABLE users ADD COLUMN display_name TEXT DEFAULT ''")

        # Таблица phrases
        await db.execute("""
            CREATE TABLE IF NOT EXISTS phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT UNIQUE
            )
        """)
        # Таблица logs
        await db.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                payload TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Таблица tickets
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                channel_id INTEGER,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

    # Загружаем фразы из файла после инициализации таблиц
    await load_phrases_from_file()


async def load_phrases_from_file():
    """Загружает фразы из templates.txt, если таблица phrases пуста."""
    # Проверяем, есть ли уже фразы в базе
    async with aiosqlite.connect(str(DB_PATH)) as db:
        async with db.execute("SELECT COUNT(*) FROM phrases") as cur:
            count = (await cur.fetchone())[0]
        if count > 0:
            print("[DB] Фразы уже есть в базе данных, загрузка из файла не требуется.")
            return

    templates_path = Path(__file__).parent / "templates.txt"
    if not templates_path.exists():
        print("[DB] Файл templates.txt не найден, загрузка фраз отменена.")
        return

    # Читаем и парсим файл
    with open(templates_path, "r", encoding="utf-8") as f:
        # Разбиваем содержимое по строкам и убираем пустые строки
        phrases = [line.strip() for line in f if line.strip()]

    if not phrases:
        print("[DB] В файле templates.txt нет фраз для загрузки.")
        return

    # Добавляем фразы в базу данных
    async with aiosqlite.connect(str(DB_PATH)) as db:
        for phrase in phrases:
            try:
                await db.execute("INSERT OR IGNORE INTO phrases (text) VALUES (?)", (phrase,))
            except Exception as e:
                print(f"[DB] Ошибка при вставке фразы '{phrase}': {e}")
        await db.commit()

    print(f"[DB] Успешно загружено {len(phrases)} фраз из файла templates.txt.")


# ... (остальные функции базы данных: add_user, update_user_display_name, get_random_phrase и т.д.)