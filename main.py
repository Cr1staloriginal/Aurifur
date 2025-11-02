import os
import asyncio
from pathlib import Path
import discord
from discord.ext import commands
import settings as config  # вместо config.py



# 🔹 Загружаем .env (если есть)
if Path('.env').exists():
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print('[INFO] .env loaded')
    except Exception:
        print('[WARN] python-dotenv not installed; skipping .env load')

import settings

# 🔹 Настройка intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# 🔹 Создаём экземпляр бота без префикса, т.к. будем использовать slash-команды
bot = commands.Bot(command_prefix='/', intents=intents)

async def load_cogs():
    for fname in Path('cogs').glob('*.py'):
        try:
            await bot.load_extension(f'cogs.{fname.stem}')  # асинхронная загрузка cogs
            print(f'Loaded cog: {fname.stem}')
        except Exception as e:
            print(f'❌ Failed loading {fname.stem}: {e}')

@bot.event
async def on_ready():
    print(f'✅ Aurifur ready as {bot.user} (id={bot.user.id})')
    try:
        await bot.tree.sync()  # синхронизация slash-команд
        print('✅ Slash-команды синхронизированы с Discord!')
    except Exception as e:
        print(f'⚠️ Ошибка при синхронизации команд: {e}')

async def main():
    await load_cogs()
    try:
        await bot.start(settings.DISCORD_TOKEN)
    except KeyboardInterrupt:
        print('🛑 Bot stopped manually')

if __name__ == '__main__':
    asyncio.run(main())
