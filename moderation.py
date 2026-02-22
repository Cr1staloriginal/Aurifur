import disnake
import asyncio
from disnake.ext import commands
from typing import Optional
from config import OWNER_ID
from typing import Any
from disnake.ext.commands import Context

MUTED_ROLE_NAME = "🔇Замьючен"


class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_check(self, ctx: Context[Any]) -> bool:
        if not isinstance(ctx.author, disnake.Member):
            return False

        perms = ctx.author.guild_permissions
        return perms.manage_messages or ctx.author.id == OWNER_ID

    @commands.command(
        name="kick",
        description="Выгнать участника."
    )
    @commands.has_permissions(kick_members=True)
    async def kick(
        self,
        ctx: Context[Any],
        member: disnake.Member,
        *,
        reason: Optional[str] = "Причина не указана"
    ) -> None:
        guild = ctx.guild
        if guild is None or guild.me is None: # pyright: ignore[reportUnnecessaryComparison]
            await ctx.send("❌ Команда доступна только на сервере.")
            return

        if member.top_role >= guild.me.top_role:
            await ctx.send("🚫 Роль пользователя выше или равна.")
            return

        if member == ctx.author:
            await ctx.send("🚫 Нельзя кикнуть себя.")
            return

        await member.kick(reason=reason)
        await ctx.send(f"👢 {member} был кикнут. Причина: {reason}")

    @commands.command(
        name="ban",
        description="Забанить участника."
    )
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        ctx: Context[Any],
        member: disnake.Member,
        *,
        reason: Optional[str] = "Причина не указана"
    ) -> None:
        guild = ctx.guild
        if guild is None or guild.me is None: # pyright: ignore[reportUnnecessaryComparison]
            return

        if member.top_role >= guild.me.top_role:
            await ctx.send("🚫 Роль пользователя выше или равна моей.")
            return

        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member} был забанен. Причина: {reason}")

    @commands.command(
        name="mute",
        description="Выдать мьют участнику."
    )
    @commands.has_permissions(manage_roles=True)
    async def mute(
        self,
        ctx: Context[Any],
        member: disnake.Member,
        minutes: int = 10,
        *,
        reason: Optional[str] = None
    ) -> None:
        guild = ctx.guild
        if guild is None or guild.me is None: # pyright: ignore[reportUnnecessaryComparison]
            return

        role = disnake.utils.get(guild.roles, name=MUTED_ROLE_NAME)
        if role is None:
            role = await guild.create_role(name=MUTED_ROLE_NAME)
            for channel in guild.channels:
                await channel.set_permissions(
                    role,
                    send_messages=False,
                    speak=False,
                    add_reactions=False
                )

        await member.add_roles(role, reason=reason)
        await ctx.send(f"🔇 {member} замучен на {minutes} минут.")

        await asyncio.sleep(minutes * 60)
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(f"🔊 {member} размучен.")

    @commands.command(
        name="purge", 
        description="Удалить последние сообщения."
    )
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: Context[Any], amount: int = 10) -> None:
        if not (1 <= amount <= 100):
            await ctx.send("❌ От 1 до 100 сообщений.")
            return

        deleted: list[disnake.Message] = await ctx.channel.purge(limit=amount + 1) # pyright: ignore[reportAttributeAccessIssue, reportUnknownMemberType, reportUnknownVariableType]
        await ctx.send(f"🧹 Удалено {len(deleted) - 1} сообщений.", delete_after=5) # pyright: ignore[reportUnknownArgumentType]


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Moderation(bot))
    print("[Moderation] Ког загружен.")