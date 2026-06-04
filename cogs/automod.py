import disnake
from disnake.ext import commands
from typing import List
import os

WORDS_FILE = os.path.join(os.path.dirname(__file__), "..", "words.txt")

def load_bad_words() -> List[str]:
    if not os.path.exists(WORDS_FILE):
        return []
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

MAX_CAPS_PERCENT = 70
MAX_REPEAT_CHARS = 10
MAX_MENTIONS = 5

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bad_words = load_bad_words()

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot or message.guild is None:
            return
        me = message.guild.me
        if not message.channel.permissions_for(me).manage_messages:
            return
        content = message.content
        if not content:
            return

        # Проверка CAPS: только для сообщений с буквами
        if len(content) >= 5:  # Повышена минимальная длина
            letters_count = sum(1 for c in content if c.isalpha())
            if letters_count > 0:
                caps_count = sum(1 for c in content if c.isupper() and c.isalpha())
                if caps_count / letters_count * 100 > MAX_CAPS_PERCENT:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention}, не пиши капсом!", delete_after=5)
                    return

        for i in range(len(content) - MAX_REPEAT_CHARS):
            seq = content[i:i+MAX_REPEAT_CHARS+1]
            if len(set(seq)) == 1 and len(seq) > MAX_REPEAT_CHARS:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, слишком много повторов!", delete_after=5)
                return

        if len(message.mentions) > MAX_MENTIONS:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, не упоминай столько людей!", delete_after=5)
            return

        lowered = content.lower()
        if any(word in lowered for word in self.bad_words):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, запрещённое слово!", delete_after=5)
            return

def setup(bot):
    bot.add_cog(AutoMod(bot))
