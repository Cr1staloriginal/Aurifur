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

# Инициализация бота (старый синтаксис)
intents = disnake.Intents.default()
intents.message_content = True
bot = disnake.Client(intents=intents)

# Добавляем атрибут command_prefix вручную (если нужны команды)
bot.command_prefix = "!"

async def shutdown():
    logger.info("Bot stopped by signal")
    await bot.close()

signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(shutdown()))

# Ручная загрузка когов (без load_extension)
async def load_cogs():
    cog_list = ["cogs.example"]
    for cog in cog_list:
        try:
            # Импортируем модуль кога
            cog_module = __import__(cog, fromlist=[cog.split(".")[-1]])
            # Получаем класс кога (предполагаем, что он назван как ExampleCog)
            cog_class = getattr(cogmodule, "ExampleCog")
            # Добавляем ког в бота
            await bot.add_cog(cog_class(bot))
            logger.info(f"[OK] Loaded cog: {cog}")
        except Exception as e:
            logger.error(f"Failed to load cog {cog}: {e}")

async def main():
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not set. Check .env file.")
        sys.exit(1)

    print(f!TOKEN LENGTH: {len(DISCORD_TOKEN)}")
    print(f!TOKEN STARTS WITH: {DISCORD_TOKEN[:10]}")

    logger.info("Loading cogs...")
    await load_cogs()  # Асинхронный вызов

    logger.info("Starting bot...")
    try:
        await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot stopped manually")
        await bot.close()
    except ConnectionClosed:
        logger.warning("Connection lost. Attempting to reconnect...")
    except Exception as e:
        logger.exception("Bot exited with an exception: %s", e)
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())


