import asyncio
import logging
import sys
import os
import signal
from dotenv import load_dotenv
import disnake
from disnake.errors import ConnectionClosed

# Загрузка переменных окружения
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота с нужными интентами
intents = disnake.Intents.default()
intents.message_content = True
bot = disnake.Client(intents=intents)

async def shutdown():
    logger.info("🛑 Bot stopped by signal")
    await bot.close()

# Обработка сигналов завершения
signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(shutdown()))

def load_cogs_sync():
    """Синхронная загрузка когов."""
    cog_list = ["cogs.example"]
    for cog in cog_list:
        try:
            bot.load_extension(cog)
            logger.info(f!✅ Loaded cog: {cog}")
        except Exception as e:
            logger.error(f!❌ Failed to load cog {cog}: {e}")

async def main():
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not set. Check .env file.")
        sys.exit(1)

    logger.info("Loading cogs...")
    load_cogs_sync()

    logger.info("Starting bot...")
    try:
        await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped manually")
        await bot.close()
    except ConnectionClosed:
        logger.warning("Connection lost. Attempting to reconnect...")
    except Exception as e:
        logger.exception("Bot exited with an exception: %s", e)
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())

