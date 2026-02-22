import disnake
from disnake.ext import commands
from typing import List, Optional


EMBED_COLOR = 0x3498DB  # Синий цвет


class Info(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.bot.help_command = None  # Отключаем встроенную help

    @commands.command(
        name="help",
        description="Показывает список всех доступных префикс-команд бота."
    )
    async def help_command(
        self,
        ctx: commands.Context,  # type: ignore[reportUnknownParameterType]  # stubs не дают точный тип Context
        command_name: Optional[str] = None
    ) -> None:
        """Красивая кастомная !help"""

        if command_name is not None:
            await ctx.send("Подробная помощь по отдельной команде пока не реализована.")
            return

        embed = disnake.Embed(
            title="📚 Справочник команд бота Aurifur",
            description=f"Все команды вызываются с префиксом **`{ctx.prefix}`**\n"
                        f"Пример: `{ctx.prefix}help`",
            color=EMBED_COLOR,
            timestamp=disnake.utils.utcnow()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url if self.bot.user else None)

        visible_cogs: int = 0

        for cog_name, cog in self.bot.cogs.items():
            if cog_name in ("automod", "info", "logs", "moderation", "selfroles", "tickets", "verification"):
                continue

            # Здесь основная проблема stubs: get_commands() возвращает List[Unknown]
            raw_commands = cog.get_commands()  # type: ignore[reportUnknownMemberType]

            # Приводим к правильному типу и фильтруем
            cog_commands: List[commands.Command] = [ # pyright: ignore[reportUnknownVariableType] # pyright: ignore[reportMissingTypeArgument] # pyright: ignore[reportMissingTypeArgument] # type: ignore
                cmd for cmd in raw_commands  # type: ignore[reportUnknownVariableType, reportUnknownMemberType]
                if not getattr(cmd, "hidden", False) # pyright: ignore[reportUnknownArgumentType]
            ]

            if not cog_commands:
                continue

            commands_list: List[str] = []
            for cmd in cog_commands:  # type: ignore[reportUnknownVariableType]
                # Все свойства cmd тоже частично Unknown в stubs
                aliases = getattr(cmd, "aliases", []) # pyright: ignore[reportUnknownArgumentType]
                aliases_str = f" (или: {', '.join(aliases)})" if aliases else ""

                desc = (
                    getattr(cmd, "description", None) # pyright: ignore[reportUnknownArgumentType]
                    or getattr(cmd, "help", None) # pyright: ignore[reportUnknownArgumentType]
                    or "Без описания"
                )

                name = getattr(cmd, "name", "?") # pyright: ignore[reportUnknownArgumentType]
                commands_list.append(f"`{ctx.prefix}{name}`{aliases_str} — {desc}")

            embed.add_field(
                name=f"🛠 {cog_name} ({len(cog_commands)} команд)", # pyright: ignore[reportUnknownArgumentType]
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