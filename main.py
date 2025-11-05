import asyncio
import logging
from pathlib import Path

import discord
from discord.ext import commands

from settings import DISCORD_TOKEN  # импортируем из исправленного settings.py

# Логирование вместо print
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aurifur")

# Загружаем .env (если есть) — уже handled в settings.py, но оставим проверку на случай
if Path(".env").exists():
    logger.info(".env detected (dotenv load handled in settings.py)")

# Настройка intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Создаём экземпляр бота (prefix можно оставить для совместимости)
bot = commands.Bot(command_prefix='/', intents=intents)


def load_cogs_sync():
    """
    Синхронно загружаем расширения (load_extension — синхронная функция в discord.py).
    Вызывается внутри асинхронного контекста.
    """
    cogs_path = Path("cogs")
    if not cogs_path.exists():
        logger.info("cogs directory not found, skipping cog loading.")
        return

    for fname in cogs_path.glob("*.py"):
        if fname.name.startswith("_"):
            continue
        ext = f"cogs.{fname.stem}"
        try:
            bot.load_extension(ext)
            logger.info("Loaded cog: %s", ext)
        except Exception:
            logger.exception("Failed loading %s", ext)


@bot.event
async def on_ready():
    logger.info("✅ Aurifur ready as %s (id=%s)", bot.user, bot.user.id)
    try:
        await bot.tree.sync()
        logger.info("✅ Slash commands synced with Discord.")
    except Exception:
        logger.exception("Error syncing slash commands")


async def main():
    # Загружаем cogs синхронно (внутри async корутины)
    load_cogs_sync()
    try:
        await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped manually")
        await bot.close()
    except Exception:
        logger.exception("Bot exited with an exception")
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
