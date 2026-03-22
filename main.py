import asyncio
asyncio.set_event_loop_policy(asyncio._WindowsProactorEventLoopPolicy())
import logging
import os
import signal
import sys
import logging
logging.basicConfig(level=logging.DEBUG)
from dotenv import load_dotenv
import disnake
from disnake.ext import commands
from disnake.errors import ConnectionClosed

# --- 0. НАСТРОЙКА ЛОГИРОВАНИЯ ---
# Выводим логи в консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- 1. НАДЕЖНАЯ ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ (.env) ---
try:
    # Определяем абсолютный путь к папке, где лежит main.py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
    DOTENV_PATH = os.path.join(BASE_DIR, '.env') 
    
    # Загружаем переменные, явно указывая путь. Это решает проблему в Pydroid 3.
    load_dotenv(DOTENV_PATH) 
    
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
except Exception as e:
    logger.error(f"Ошибка при загрузке .env файла: {e}")
    sys.exit(1)


# --- 2. ИНИЦИАЛИЗАЦИЯ БОТА ---
# Намерения (Intents)
intents = disnake.Intents.default()
# Обязательно, если бот должен читать содержимое сообщений
intents.message_content = True 

# Инициализация бота с префиксом и интентами
bot = commands.Bot(command_prefix="=", intents=intents) 

# --- 3. ОБРАБОТЧИК СОБЫТИЯ ГОТОВНОСТИ ---
@bot.event
async def on_ready():
    # Статус бота при запуске
    logger.info(f"Бот успешно вошел как: {bot.user} (ID: {bot.user.id})")
    print("-" * 30)
    print(f"Готов к работе!")
    print(f"Пригласительная ссылка: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=8&scope=bot%20applications.commands")
    print("-" * 30)

# --- 4. ФУНКЦИЯ ЗАГРУЗКИ КОГОВ ---
def load_cogs():
    # Путь к папке cogs относительно BASE_DIR
    cogs_dir = os.path.join(BASE_DIR, "cogs")

    if not os.path.isdir(cogs_dir):
        logger.warning(f"Папка 'cogs' не найдена по пути: {cogs_dir}")
        return

    # Получаем список Python-файлов в папке cogs (игнорируя __init__.py)
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            # Формируем имя кога в виде 'cogs.имя_файла'
            cog_name = f"cogs.{filename[:-3]}"
            try:
                bot.load_extension(cog_name)
                logger.info(f"[OK] Загружен ког: {cog_name}")
            except Exception as e:
                # В логах будет видно, если в коге есть синтаксическая ошибка или нет функции setup()
                logger.error(f"Не удалось загрузить ког {cog_name}: {e}")

# --- 5. ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА (MAIN) ---
async def main():
    if not DISCORD_TOKEN:
        logger.error("КРИТИЧЕСКАЯ ОШИБКА: DISCORD_TOKEN не загружен. Проверьте .env файл.")
        sys.exit(1)

    # Синхронная загрузка когов
    load_cogs() 

    logger.info("Попытка подключения к Discord...")
    try:
        # Использование bot.start() для обработки переподключений
        await bot.start(DISCORD_TOKEN) 
    except disnake.errors.LoginFailure:
        logger.error("ОШИБКА АВТОРИЗАЦИИ: Передан неверный токен. Сбросьте токен.")
        sys.exit(1)
    except ConnectionClosed:
        logger.warning("Соединение потеряно. Попытка переподключения...")
    except Exception:
        logger.exception("Бот завершился с непредвиденным исключением.")
    finally:
        # Эта часть выполняется только при полном завершении (например, после bot.close())
        logger.info("Бот остановлен.")


# --- 6. ЗАПУСК ПРОГРАММЫ ---
if __name__ == "__main__":
    async def shutdown_handler(signal_name: str) -> None:
        logger.info(f"Получен сигнал {signal_name}. Graceful shutdown...")
        if bot and not bot.is_closed():
            await bot.close()
        # sys.exit(0) здесь не нужен — asyncio.run завершится сам

    async def main_with_signals():
        if not DISCORD_TOKEN:
            logger.error("КРИТИЧЕСКАЯ ОШИБКА: DISCORD_TOKEN не загружен. Проверьте .env файл.")
            sys.exit(1)

        load_cogs()

        logger.info("Попытка подключения к Discord...")

        # Получаем текущий event loop
        loop = asyncio.get_running_loop()

        # Настраиваем обработчики сигналов ПРАВИЛЬНО
        if os.name != 'nt':  # Только на Unix-подобных (Linux, macOS, Android/Termux)
            for sig in (signal.SIGINT, signal.SIGTERM):
                loop.add_signal_handler(
                    sig,
                    lambda s=sig: asyncio.create_task(shutdown_handler(signal.Signals(s).name))
                )

        try:
            await bot.start(DISCORD_TOKEN)
        except disnake.errors.LoginFailure:
            logger.error("ОШИБКА АВТОРИЗАЦИИ: Неверный токен.")
            sys.exit(1)
        except Exception:
            logger.exception("Неожиданная ошибка во время работы бота.")
        finally:
            logger.info("Бот остановлен.")

    try:
        asyncio.run(main_with_signals())
    except KeyboardInterrupt:
        # Это уже не сработает (перехватывается add_signal_handler), но на всякий случай
        logger.info("Прервано пользователем.")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")