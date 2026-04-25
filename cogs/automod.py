from __future__ import annotations

import re
from pathlib import Path
from typing import Final

import disnake
from disnake.ext import commands

BAD_WORDS_FILE: Final[Path] = Path(__file__).resolve().parent.parent / "data" / "words.txt"
MAX_CAPS_PERCENT: Final[int] = 70
MAX_REPEAT_CHARS: Final[int] = 10
MAX_MENTIONS: Final[int] = 5
REPEATED_CHARS_PATTERN: Final[re.Pattern[str]] = re.compile(rf"(.)\\1{{{MAX_REPEAT_CHARS},}}")


class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bad_words = self._load_bad_words()

    @staticmethod
    def _load_bad_words() -> set[str]:
        if not BAD_WORDS_FILE.exists():
            return set()

        return {
            line.strip().lower()
            for line in BAD_WORDS_FILE.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.strip().startswith("#")
        }

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message) -> None:
        if message.author.bot or message.guild is None:
            return

        me = message.guild.me
        if me is None or not message.channel.permissions_for(me).manage_messages:
            return

        content = message.content

        if len(content) > 10:
            letters = [c for c in content if c.isalpha()]
            if letters:
                caps_count = sum(1 for c in letters if c.isupper())
                if caps_count / len(letters) * 100 > MAX_CAPS_PERCENT:
                    await message.delete()
                    await message.channel.send(
                        f"{message.author.mention}, пожалуйста, не пиши капсом!",
                        delete_after=5,
                    )
                    return

        if REPEATED_CHARS_PATTERN.search(content):
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, слишком много повторяющихся символов!",
                delete_after=5,
            )
            return

        if len(message.mentions) > MAX_MENTIONS:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, не упоминай так много людей сразу!",
                delete_after=5,
            )
            return

        lowered_content = content.lower()
        if self.bad_words and any(word in lowered_content for word in self.bad_words):
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, запрещённое слово в сообщении!",
                delete_after=5,
            )
            return

        await self.bot.process_commands(message)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AutoMod(bot))
