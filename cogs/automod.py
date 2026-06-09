import disnake
from disnake.ext import commands
import os
import time
from collections import defaultdict

WORDS_FILE = os.path.join(os.path.dirname(__file__), "..", "words.txt")

def load_bad_words():
    if not os.path.exists(WORDS_FILE):
        return []
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

# Ключевые слова для политики/религии
POLITICS_RELIGION_WORDS = [
    "путин", "навальный", "зеленский", "коммунизм", "капитализм", "социализм",
    "ислам", "христианство", "буддизм", "религия", "политика", "нацизм", "фашизм"
]

MAX_CAPS_PERCENT = 70
MAX_REPEAT_CHARS = 10
MAX_MENTIONS = 5
MESSAGE_SPAM_LIMIT = 4
SPAM_WINDOW = 5
SHORTENERS = ['bit.ly', 'goo.gl', 'tinyurl.com', 'clck.ru', 'is.gd']

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        self.bad_words = load_bad_words()
        self.user_messages = defaultdict(list)

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.author.bot or message.guild is None:
            return
        if not message.channel.permissions_for(message.guild.me).manage_messages:
            return

        content = message.content
        if not content:
            return

        violation = None
        rule_name = None

        # Капс
        if len(content) > 10:
            caps = sum(1 for c in content if c.isupper())
            caps_percent = caps / len(content) * 100
            if caps_percent > MAX_CAPS_PERCENT:
                violation = f"Капс ({caps_percent:.0f}%)"
                rule_name = "📜 Правило 1.1: Относись с уважением"

        # Повторы символов
        if not violation:
            for i in range(len(content) - MAX_REPEAT_CHARS):
                seq = content[i:i+MAX_REPEAT_CHARS+1]
                if len(set(seq)) == 1:
                    violation = f"Повтор символа '{seq[0]}'"
                    rule_name = "📜 Правило 2.2: Спам, флуд и оффтоп запрещены"
                    break

        # Упоминания
        if not violation and len(message.mentions) > MAX_MENTIONS:
            violation = f"Массовое упоминание ({len(message.mentions)})"
            rule_name = "📜 Правило 2.2: Спам, флуд и оффтоп запрещены"

        # Запрещённые слова
        if not violation:
            lowered = content.lower()
            for word in self.bad_words:
                if word in lowered:
                    violation = f"Запрещённое слово: {word}"
                    rule_name = "📜 Правило 2.1: Сервер полностью SFW"
                    break

        # Политика/религия
        if not violation:
            lowered = content.lower()
            for word in POLITICS_RELIGION_WORDS:
                if word in lowered:
                    violation = f"Запрещённая тема: {word}"
                    rule_name = "📜 Правило 1.4: Политика, религия и идеологии запрещены"
                    break

        # Спам по времени
        if not violation:
            now = time.time()
            self.user_messages[message.author.id].append(now)
            self.user_messages[message.author.id] = [t for t in self.user_messages[message.author.id] if now - t < SPAM_WINDOW]
            if len(self.user_messages[message.author.id]) > MESSAGE_SPAM_LIMIT:
                violation = f"Спам ({len(self.user_messages[message.author.id])} сообщений за {SPAM_WINDOW} сек)"
                rule_name = "📜 Правило 2.2: Спам, флуд и оффтоп запрещены"

        # Сокращённые ссылки
        if not violation:
            for shortener in SHORTENERS:
                if shortener in content.lower():
                    violation = f"Сокращённая ссылка ({shortener})"
                    rule_name = "📜 Правило 4.4: Сокращённые ссылки запрещены"
                    break

        if violation:
            try:
                await message.delete()
            except:
                pass
            await message.channel.send(
                f"{message.author.mention} ⚠️ **Нарушение правил!**\n"
                f"📋 **{rule_name}**\n"
                f"❌ {violation}\n"
                f"🔔 Вам выдано предупреждение. Администрация рассмотрит наказание.",
                delete_after=10
            )
            warns_cog = self.bot.get_cog("Warns")
            if warns_cog:
                await warns_cog.send_warn_to_mod_channel(
                    user_id=message.author.id,
                    reason=violation,
                    rule_name=rule_name,
                    message_link=message.jump_url
                )

def setup(bot):
    bot.add_cog(AutoMod(bot))