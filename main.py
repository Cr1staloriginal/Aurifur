import asyncio
import logging
import os
import signal
import sys
from pathlib import Path

import disnake
from disnake.errors import ConnectionClosed
from disnake.ext import commands
from dotenv import load_dotenv

# Windows-specific event loop policy for better subprocess/signal compatibility.
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
DOTENV_PATH = BASE_DIR / ".env"


def load_environment() -> str:
    """Load environment variables and return Discord token."""
    try:
        load_dotenv(DOTENV_PATH)
    except Exception as exc:
        logger.error("Ошибка при загрузке .env файла: %s", exc)
        sys.exit(1)

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("КРИТИЧЕСКАЯ ОШИБКА: DISCORD_TOKEN не загружен. Проверьте .env файл.")
        sys.exit(1)
    return token


def create_bot() -> commands.Bot:
    intents = disnake.Intents.default()
    intents.message_content = True
    return commands.Bot(command_prefix="=", intents=intents)


bot = create_bot()


@bot.event
async def on_ready() -> None:
    logger.info("Бот успешно вошел как: %s (ID: %s)", bot.user, bot.user.id)
    print("-" * 30)
    print("Готов к работе!")
    print(
        "Пригласительная ссылка: "
        f"https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands"
    )
    print("-" * 30)


def load_cogs() -> None:
    cogs_dir = BASE_DIR / "cogs"
    if not cogs_dir.is_dir():
        logger.warning("Папка 'cogs' не найдена по пути: %s", cogs_dir)
        return

    for cog_file in cogs_dir.glob("*.py"):
        if cog_file.name.startswith("_"):
            continue

        cog_name = f"cogs.{cog_file.stem}"
        try:
            bot.load_extension(cog_name)
            logger.info("[OK] Загружен ког: %s", cog_name)
        except Exception as exc:
            logger.error("Не удалось загрузить ког %s: %s", cog_name, exc)


async def shutdown_handler(signal_name: str) -> None:
    logger.info("Получен сигнал %s. Graceful shutdown...", signal_name)
    if not bot.is_closed():
        await bot.close()


async def main() -> None:
    discord_token = load_environment()
    load_cogs()

    loop = asyncio.get_running_loop()
    if os.name != "nt":
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(shutdown_handler(signal.Signals(s).name)),
            )

    logger.info("Попытка подключения к Discord...")
    try:
        await bot.start(discord_token)
    except disnake.errors.LoginFailure:
        logger.error("ОШИБКА АВТОРИЗАЦИИ: Неверный токен.")
        sys.exit(1)
    except ConnectionClosed:
        logger.warning("Соединение потеряно. Попытка переподключения...")
    except Exception:
        logger.exception("Неожиданная ошибка во время работы бота.")
    finally:
        logger.info("Бот остановлен.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Прервано пользователем.")
