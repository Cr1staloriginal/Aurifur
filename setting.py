import os
from pathlib import Path

# Опционально загружаем .env если он есть (требует python-dotenv как dev-зависимость)
if Path(".env").exists():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        # dotenv не обязателен — окружение может быть настроено другими способами
        pass

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN is not set. Set it in environment or in .env file.")

# Путь к файлу БД по умолчанию (можно переопределить через переменную окружения)
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/database.db")