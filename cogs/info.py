import disnake
from disnake.ext import commands
from typing import List, Optional

EMBED_COLOR = 0x3498DB

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.bot.help_command = None  # Отключаем встроенную help

    @commands.command(name="help", description="Показывает список всех доступных префикс-команд бота.")
    async def help_command(self, ctx: commands.Context, command_name: Optional[str] = None) -> None:
        if command_name is not None:
            await ctx.send("Подробная помощь по отдельной команде пока не реализована.")
            return

        embed = disnake.Embed(
            title="📚 Справочник команд бота Aurifur",
            description=f"Все команды вызываются с префиксом **`{ctx.prefix}`**\nПример: `{ctx.prefix}help`",
            color=EMBED_COLOR,
            timestamp=disnake.utils.utcnow()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url if self.bot.user else None)

        visible_cogs = 0
        for cog_name, cog in self.bot.cogs.items():
            # Показываем все коги, кроме самого себя (info) чтобы не зацикливать
            if cog_name.lower() == "info":
                continue
            raw_commands = cog.get_commands()
            cog_commands = [cmd for cmd in raw_commands if not getattr(cmd, "hidden", False)]
            if not cog_commands:
                continue

            commands_list = []
            for cmd in cog_commands:
                aliases = getattr(cmd, "aliases", [])
                aliases_str = f" (или: {', '.join(aliases)})" if aliases else ""
                desc = getattr(cmd, "description", None) or getattr(cmd, "help", None) or "Без описания"
                name = getattr(cmd, "name", "?")
                commands_list.append(f"`{ctx.prefix}{name}`{aliases_str} — {desc}")

            embed.add_field(
                name=f"🛠 {cog_name} ({len(cog_commands)} команд)",
                value="\n".join(commands_list),
                inline=False
            )
            visible_cogs += 1

        if visible_cogs == 0:
            embed.description = f"На данный момент префикс-команды с `{ctx.prefix}` не загружены."

        embed.set_footer(
            text=f"Модулей с командами: {visible_cogs} • Запрошено: {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )
        await ctx.send(embed=embed)

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Info(bot))
    print("[Info] Ког с кастомной командой !help успешно загружен.")