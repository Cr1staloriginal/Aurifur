import disnake
from disnake.ext import commands
from typing import List
import os

#Плохие слова для Автомода
BAD_WORDS_FILE = os.path.join(os.path.dirname(__file__), "--", "words.txt")
# Список запрещённых слов (можно вынести в отдельный файл или БД позже)
BAD_WORDS: List[str] = [
    "плохое_слово1",
    "плохое_слово2",
    # добавь свои
]
# Настройки автомодерации
MAX_CAPS_PERCENT = 70      # Максимальный % заглавных букв
MAX_REPEAT_CHARS = 10      # Максимум повторяющихся символов подряд
MAX_MENTIONS = 5           # Максимум упоминаний в одном сообщении

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message) -> None:
        # Игнорируем ботов и сообщения в ЛС
        if message.author.bot or message.guild is None:
            return

        # Проверяем права бота (чтобы не пытаться удалять без прав)
        me: disnake.Member = message.guild.me
        if not message.channel.permissions_for(me).manage_messages:
            return

        content: str = message.content

        # 1. Проверка на капс
        if len(content) > 10:  # Только для длинных сообщений
            caps_count = sum(1 for c in content if c.isupper())
            if caps_count / len(content) * 100 > MAX_CAPS_PERCENT:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention}, пожалуйста, не пиши капсом!", delete_after=5
                )
                return

        # 2. Проверка на повторяющиеся символы (типа "аааааааааа")
        if any(len(seq) > MAX_REPEAT_CHARS for seq in [content[i:i+MAX_REPEAT_CHARS+1] for i in range(len(content)-MAX_REPEAT_CHARS)] if len(set(seq)) == 1):
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, слишком много повторяющихся символов!", delete_after=5
            )
            return

        # 3. Проверка на слишком много упоминаний
        if len(message.mentions) > MAX_MENTIONS:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, не упоминай так много людей сразу!", delete_after=5
            )
            return

        # 4. Проверка на запрещённые слова
        lowered_content: str = content.lower()
        if any(word in lowered_content for word in BAD_WORDS):
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, запрещённое слово в сообщении!", delete_after=5
            )
            return

        # Если всё ок — передаём дальше (для префикс-команд)
        await self.bot.process_commands(message)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AutoMod(bot))