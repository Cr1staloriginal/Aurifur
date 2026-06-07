import aiosqlite
from pathlib import Path
import os
import datetime
from typing import Optional

DATABASE_PATH = os.getenv("DATABASE_PATH", "data/database.db")
DB_PATH = Path(DATABASE_PATH)


async def init_db() -> None:
    """Инициализация всех таблиц"""
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
        # Таблица warns (НОВАЯ)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                moderator_id INTEGER NOT NULL,
                reason TEXT,
                rule_name TEXT,
                message_link TEXT,
                date TEXT,
                action_taken TEXT DEFAULT 'pending'
            )
        """)
        await db.commit()

    await load_phrases_from_file()


async def load_phrases_from_file():
    """Загружает фразы из templates.txt в таблицу phrases, если она пуста"""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        async with db.execute("SELECT COUNT(*) FROM phrases") as cur:
            count = (await cur.fetchone())[0]
        if count > 0:
            return

    templates_path = Path(__file__).parent / "templates.txt"
    if not templates_path.exists():
        print("[DB] templates.txt не найден")
        return

    with open(templates_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() if "{nick}" in line]

    async with aiosqlite.connect(str(DB_PATH)) as db:
        for line in lines:
            await db.execute("INSERT OR IGNORE INTO phrases (text) VALUES (?)", (line,))
        await db.commit()
    print(f"[DB] Загружено {len(lines)} фраз")


# ========== Работа с варнами ==========

async def add_warn(user_id: int, moderator_id: int, reason: str, rule_name: str = None, message_link: str = None) -> int:
    """Добавляет предупреждение. Возвращает ID варна."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute("""
            INSERT INTO warns (user_id, moderator_id, reason, rule_name, message_link, date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, moderator_id, reason, rule_name, message_link, datetime.datetime.now().isoformat()))
        await db.commit()
        return cursor.lastrowid


async def get_user_warns(user_id: int) -> list:
    """Возвращает все предупреждения пользователя."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        async with db.execute("SELECT * FROM warns WHERE user_id = ? ORDER BY date DESC", (user_id,)) as cur:
            return await cur.fetchall()


async def get_warn(warn_id: int):
    """Возвращает одно предупреждение по ID."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        async with db.execute("SELECT * FROM warns WHERE id = ?", (warn_id,)) as cur:
            return await cur.fetchone()


async def update_warn_action(warn_id: int, action: str) -> None:
    """Обновляет поле action_taken (ban/kick/mute/dismissed)."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute("UPDATE warns SET action_taken = ? WHERE id = ?", (action, warn_id))
        await db.commit()


async def remove_warn(warn_id: int) -> bool:
    """Удаляет предупреждение."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute("DELETE FROM warns WHERE id = ?", (warn_id,))
        await db.commit()
        return cursor.rowcount > 0


async def clear_user_warns(user_id: int) -> int:
    """Удаляет все предупреждения пользователя."""
    async with aiosqlite.connect(str(DB_PATH)) as db:
        cursor = await db.execute("DELETE FROM warns WHERE user_id = ?", (user_id,))
        await db.commit()
        return cursor.rowcount


# ========== Остальные функции ==========

async def update_user_display_name(user_id: int, display_name: str) -> None:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute(
            "UPDATE users SET display_name = ?, last_seen = CURRENT_TIMESTAMP WHERE user_id = ?",
            (display_name, user_id)
        )
        await db.commit()


async def get_random_phrase() -> str:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        async with db.execute("SELECT text FROM phrases ORDER BY RANDOM() LIMIT 1") as cur:
            row = await cur.fetchone()
            return row[0] if row else "🐾 {nick} приветствует тебя!"


async def log_event(event_type: str, payload: str) -> None:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute(
            "INSERT INTO logs (event_type, payload) VALUES (?, ?)",
            (event_type, payload)
        )
        await db.commit()