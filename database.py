import aiosqlite
from pathlib import Path
from typing import Optional

from config import DATABASE_PATH

DB_PATH = Path(DATABASE_PATH)


async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                verified INTEGER DEFAULT 0,
                points INTEGER DEFAULT 0,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS phrases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT UNIQUE
            )
            """
        )

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                payload TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                channel_id INTEGER,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        await db.commit()


async def add_phrase(text: str) -> None:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute("INSERT OR IGNORE INTO phrases (text) VALUES (?)", (text,))
        await db.commit()


async def get_random_phrase() -> Optional[str]:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        async with db.execute("SELECT text FROM phrases ORDER BY RANDOM() LIMIT 1") as cur:
            row = await cur.fetchone()
            return row[0] if row else None


async def log_event(event_type: str, payload: str) -> None:
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.execute(
            "INSERT INTO logs (event_type, payload) VALUES (?, ?)",
            (event_type, payload)
        )
        await db.commit()
