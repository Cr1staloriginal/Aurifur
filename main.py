import asyncio
import logging
import sys
import os
from dotenv import load_dotenv
import disnake

# Загрузка переменных окружения
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = disnake.Client(intents=disnake.Intents.all())

async def main():
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not set. Check settings.py or .env.")
        sys.exit(1)

    load_cogs_sync()  # или await load_cogs_sync(), если функция асинхронная

    try:
        await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped manually")
        await bot.close()
    except Exception as e:
        logger.exception("Bot exited with an exception: %s", e)
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
