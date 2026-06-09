import asyncio
import logging
import os
import sys
from dotenv import load_dotenv
import disnake
from disnake.ext import commands

# --- 1. Настройка логирования ---
# Настраиваем логирование, чтобы видеть, что происходит с ботом.
# Информация будет выводиться в консоль в понятном формате.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- 2. Загрузка переменных окружения ---
# Определяем путь к корневой папке проекта для надёжности.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOTENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(DOTENV_PATH)

# Получаем токен, без него работа невозможна.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    # Если токен не найден, выводим сообщение и завершаем работу.
    logger.error("DISCORD_TOKEN не найден в файле .env!")
    sys.exit(1)

# --- 3. Настройка Intents (намерений) ---
# Намерения говорят Discord, какие события бот должен получать.
intents = disnake.Intents.default()
intents.message_content = True  # для чтения содержимого сообщений
intents.members = True          # для отслеживания новых/ушедших участников
intents.voice_states = True     # для работы с голосовыми каналами

# --- 4. Создание экземпляра бота ---
# InteractionBot — правильный выбор для бота на слеш-командах.
bot = commands.InteractionBot(intents=intents)

# --- 5. Диспетчер логов ---
# Подключаем LogDispatcher из utils, чтобы отправлять сообщения в нужные каналы.
from utils.log_dispatcher import LogDispatcher
bot.log_dispatcher = LogDispatcher(bot)

# --- 6. Инициализация базы данных ---
from database import init_db

@bot.event
async def on_ready():
    # Выполняем асинхронную инициализацию БД при запуске.
    await init_db()
    logger.info(f"Бот успешно запущен: {bot.user} (ID: {bot.user.id})")
    print("-" * 30)
    print("Готов к работе!")
    print("-" * 30)

# --- 7. Загрузка модулей (cogs) ---
def load_cogs():
    # Загружаем все коги из папки cogs, игнорируя пустые файлы и ошибки.
    for filename in os.listdir(BASE_DIR):
        if filename.endswith(".py") and not filename.startswith("_"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                bot.load_extension(cog_name)
                logger.info(f"[OK] Загружен модуль: {cog_name}")
            except Exception as e:
                # Логируем ошибку загрузки, но не останавливаем бота.
                logger.error(f"[ERROR] Не удалось загрузить {cog_name}: {e}")

# --- 8. Запуск бота ---
if __name__ == "__main__":
    load_cogs()  # Загружаем модули перед запуском
    logger.info("Бот запускается...")
    try:
        # Запускаем бота. Все последующие ошибки будут обработаны здесь.
        bot.run(DISCORD_TOKEN)
    except KeyboardInterrupt:
        # Обрабатываем остановку через Ctrl+C.
        logger.info("Бот остановлен вручную.")
    except Exception as e:
        # Логируем любую другую критическую ошибку.
        logger.error(f"Произошла критическая ошибка: {e}")