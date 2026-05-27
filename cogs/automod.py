import disnake
from disnake.ext import commands
from typing import List
import os

# Путь к файлу со стоп-словами (words.txt лежит в корне проекта)
WORDS_FILE = os.path.join(os.path.dirname(__file__), "..", "words.txt")

def load_bad_words() -> List[str]:
    """Загружает список запрещённых слов из файла words.txt"""
    if not os.path.exists(WORDS_FILE):
        return []
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

# Настройки автомодерации
MAX_CAPS_PERCENT = 70
MAX_REPEAT_CHARS = 10
MAX_MENTIONS = 5

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bad_words = load_bad_words()

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message) -> None:
        if message.author.bot or message.guild is None:
            return

        me = message.guild.me
        if not message.channel.permissions_for(me).manage_messages:
            return

        content = message.content
        if not content:
            return

        # 1. Капс
        if len(content) > 10:
            caps_count = sum(1 for c in content if c.isupper())
            if caps_count / len(content) * 100 > MAX_CAPS_PERCENT:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, пожалуйста, не пиши капсом!", delete_after=5)
                return

        # 2. Повторяющиеся символы
        for i in range(len(content) - MAX_REPEAT_CHARS):
            seq = content[i:i+MAX_REPEAT_CHARS+1]
            if len(set(seq)) == 1 and len(seq) > MAX_REPEAT_CHARS:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, слишком много повторяющихся символов!", delete_after=5)
                return

        # 3. Упоминания
        if len(message.mentions) > MAX_MENTIONS:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, не упоминай так много людей сразу!", delete_after=5)
            return

        # 4. Запрещённые слова
        lowered = content.lower()
        if any(word in lowered for word in self.bad_words):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, запрещённое слово в сообщении!", delete_after=5)
            return

        await self.bot.process_commands(message)

def setup(bot: commands.Bot) -> None:
    bot.add_cog(AutoMod(bot))