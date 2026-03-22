import aiosqlite
from pathlib import Path
from typing import Optional

# Импортируйте путь к БД из settings.py
try:
    from settings import DATABASE_PATH
except ImportError:
    # Фолбэк: если settings.py не найден, используем дефолтный путь
    DATABASE_PATH = "data/database.db" # type: ignore

DB_PATH = Path(DATABASE_PATH)

# Асинхронная инициализация БД
async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                verified INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT UNIQUE
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                payload TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
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

# Добавление фразы
async def add_phrase(text: str) -> None:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute("INSERT OR IGNORE INTO phrases (text) VALUES (?)", (text,))
        await db.commit()

# Получение случайной фразы
async def get_random_phrase() -> Optional[str]:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        async with db.execute("SELECT text FROM phrases ORDER BY RANDOM() LIMIT 1") as cur:
            row = await cur.fetchone()
            return row[0] if row else None

# Логирование события — эту функцию импортируют ваши cogs!
async def log_event(event_type: str, payload: str) -> None:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute(
            "INSERT INTO logs (event_type, payload) VALUES (?, ?)",
            (event_type, payload),
        )
        await db.commit()

# Пример функции для создания пользователя
async def add_user(user_id: int, username: str) -> None:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db.commit()

# Пример функции для обновления информации о пользователе
async def update_user(user_id: int, **kwargs) -> None: # type: ignore
    fields = ', '.join(f"{k}=?" for k in kwargs)
    values = list(kwargs.values()) # type: ignore
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute(
            f"UPDATE users SET {fields} WHERE user_id=?",
            (*values, user_id)
        )
        await db.commit()