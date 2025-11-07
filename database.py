async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    async with aiosqlite.connect(str(DB_PATH)) as db:
        # Создание таблиц (как в оригинале)
        # ...

        # Индексы
        await db.execute("CREATE INDEX IF NOT EXISTS idx_phrases_text ON phrases (text)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_logs_created ON logs (created_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_tickets_user ON tickets (user_id)")
        
        await db.commit()
async def add_phrase(text: str) -> None:
    if not text or len(text.strip()) == 0:
        raise ValueError("Phrase cannot be empty")
    if len(text) > 1000:
        raise ValueError("Phrase is too long (max 1000 chars)")

    try:
        async with aiosqlite.connect(str(DB_PATH)) as db:
            await db.execute(
                "INSERT OR IGNORE INTO phrases (text) VALUES (?)",
                (text.strip(),)
            )
            await db.commit()
    except aiosqlite.Error as e:
        logger.error("DB error when adding phrase '%s': %s", text, e)
        raise
