import disnake
import asyncio
from disnake.ext import commands
from typing import Optional, Any
from disnake.ext.commands import Context
import os

MUTED_ROLE_NAME = "🔇Замьючен"
OWNER_ID = int(os.getenv("OWNER_ID", 0))

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: Context[Any]) -> bool:
        if not isinstance(ctx.author, disnake.Member):
            return False
        return ctx.author.guild_permissions.manage_messages or ctx.author.id == OWNER_ID

    @commands.command(name="kick", description="Выгнать участника.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: Context[Any], member: disnake.Member, *, reason: Optional[str] = "Не указана"):
        guild = ctx.guild
        if not guild or not guild.me:
            await ctx.send("❌ Доступно только на сервере.")
            return
        if member.top_role >= guild.me.top_role:
            await ctx.send("🚫 Роль выше моей.")
            return
        if member == ctx.author:
            await ctx.send("🚫 Нельзя кикнуть себя.")
            return

        await member.kick(reason=reason)
        await ctx.send(f"👢 {member} кикнут. Причина: {reason}")

        embed = disnake.Embed(title="🔨 Кик", color=disnake.Color.red(), timestamp=disnake.utils.utcnow())
        embed.add_field(name="Участник", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Модератор", value=ctx.author.mention, inline=False)
        embed.add_field(name="Причина", value=reason, inline=False)
        await self.bot.log_dispatcher.send("mod", embed)

    @commands.command(name="ban", description="Забанить участника.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: Context[Any], member: disnake.Member, *, reason: Optional[str] = "Не указана"):
        guild = ctx.guild
        if not guild or not guild.me:
            return
        if member.top_role >= guild.me.top_role:
            await ctx.send("🚫 Роль выше моей.")
            return
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member} забанен. Причина: {reason}")

        embed = disnake.Embed(title="🔨 Бан", color=disnake.Color.dark_red(), timestamp=disnake.utils.utcnow())
        embed.add_field(name="Участник", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Модератор", value=ctx.author.mention, inline=False)
        embed.add_field(name="Причина", value=reason, inline=False)
        await self.bot.log_dispatcher.send("mod", embed)

    @commands.command(name="mute", description="Выдать мьют участнику.")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx: Context[Any], member: disnake.Member, minutes: int = 10, *, reason: Optional[str] = None):
        guild = ctx.guild
        if not guild or not guild.me:
            return
        role = disnake.utils.get(guild.roles, name=MUTED_ROLE_NAME)
        if role is None:
            role = await guild.create_role(name=MUTED_ROLE_NAME)
            for channel in guild.channels:
                await channel.set_permissions(role, send_messages=False, speak=False, add_reactions=False)
        await member.add_roles(role, reason=reason)
        await ctx.send(f"🔇 {member} замучен на {minutes} мин.")

        embed = disnake.Embed(title="🔇 Мут", color=disnake.Color.orange(), timestamp=disnake.utils.utcnow())
        embed.add_field(name="Участник", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Модератор", value=ctx.author.mention, inline=False)
        embed.add_field(name="Длительность", value=f"{minutes} мин.", inline=False)
        embed.add_field(name="Причина", value=reason or "Не указана", inline=False)
        await self.bot.log_dispatcher.send("mod", embed)

        await asyncio.sleep(minutes * 60)
        if role in member.roles:
            await member.remove_roles(role)
            await ctx.send(f"🔊 {member} размучен.")

    @commands.command(name="purge", description="Удалить сообщения.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: Context[Any], amount: int = 10):
        if not (1 <= amount <= 100):
            await ctx.send("❌ От 1 до 100.")
            return
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 Удалено {len(deleted) - 1} сообщений.", delete_after=5)

        embed = disnake.Embed(title="🧹 Очистка чата", color=disnake.Color.purple(), timestamp=disnake.utils.utcnow())
        embed.add_field(name="Канал", value=ctx.channel.mention, inline=False)
        embed.add_field(name="Модератор", value=ctx.author.mention, inline=False)
        embed.add_field(name="Удалено сообщений", value=str(len(deleted) - 1), inline=False)
        await self.bot.log_dispatcher.send("mod", embed)

def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))