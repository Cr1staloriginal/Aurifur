import discord
from discord.ext import commands
import re
from database import log_event
import os

CAPS_THRESHOLD = 0.7
BANNED_FILE = "data/words.txt"

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent = {}
        self.banned_words = self.load_banned_words()

    def load_banned_words(self):
        """Загружает список запрещённых слов из файла."""
        if not os.path.exists(BANNED_FILE):
            os.makedirs(os.path.dirname(BANNED_FILE), exist_ok=True)
            with open(BANNED_FILE, "w", encoding="utf-8") as f:
                f.write("# Добавляй сюда запрещённые слова, одно в строку.\n")
            print(f"[AutoMod] Файл {BANNED_FILE} создан (пока пустой).")

        with open(BANNED_FILE, "r", encoding="utf-8") as f:
            words = [line.strip().lower() for line in f if line.strip() and not line.startswith("#")]
        print(f"[AutoMod] Загружено {len(words)} запрещённых слов.")
        return words

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        content = message.content or ''
        lower = content.lower()

        # Проверка на запрещённые слова
        for w in self.banned_words:
            if w in lower:
                try:
                    await message.delete()
                    await message.channel.send(
                        f'{message.author.mention}, запрещённое слово обнаружено.',
                        delete_after=5
                    )
                    await log_event('automod_banned', f'{message.author.id}|{w}')
                    return
                except discord.Forbidden:
                    print("[AutoMod] Нет прав на удаление сообщения.")
                    return

        # Проверка на капс
        letters = [c for c in content if c.isalpha()]
        if letters:
            caps_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
            if caps_ratio > CAPS_THRESHOLD and len(letters) > 6:
                try:
                    await message.delete()
                    await message.channel.send(
                        f'{message.author.mention}, пожалуйста, не пиши капсом.',
                        delete_after=5
                    )
                    await log_event('automod_caps', f'{message.author.id}|{content}')
                    return
                except discord.Forbidden:
                    print("[AutoMod] Нет прав на удаление капс-сообщения.")
                    return

        # Проверка на спам
        user = message.author.id
        cnt = self.recent.get(user, 0) + 1
        self.recent[user] = cnt

        if cnt > 6:
            await message.channel.send(
                f'{message.author.mention}, перестань флудить.',
                delete_after=5
            )
            await log_event('automod_spam', f'{message.author.id}')
            self.recent[user] = 0

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
