from __future__ import annotations

import asyncio
from typing import Final

import disnake
from disnake.ext import commands

from database import log_event

TICKET_CATEGORY: Final[str] = "Тикеты"
STAFF_ROLES: Final[tuple[str, ...]] = (
    "🦊 Хвостик порядка",
    "🦊 Старший хвостик",
    "🐾 Младшая лапка",
    "🐾 Старшая лапка",
    "🐾 Главная лапка",
)


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @staticmethod
    def _build_overwrites(guild: disnake.Guild, author: disnake.Member) -> dict[disnake.Role | disnake.Member, disnake.PermissionOverwrite]:
        overwrites: dict[disnake.Role | disnake.Member, disnake.PermissionOverwrite] = {
            guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            author: disnake.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        for role_name in STAFF_ROLES:
            role = disnake.utils.get(guild.roles, name=role_name)
            if role is not None:
                overwrites[role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)

        return overwrites

    @commands.command(name="ticket", description="Создать тикет.")
    async def ticket(self, ctx: commands.Context, *, reason: str | None = None) -> None:
        if ctx.guild is None or not isinstance(ctx.author, disnake.Member):
            await ctx.send("❌ Команда доступна только на сервере.")
            return

        guild = ctx.guild
        category = disnake.utils.get(guild.categories, name=TICKET_CATEGORY)
        if category is None:
            category = await guild.create_category(TICKET_CATEGORY)

        channel = await guild.create_text_channel(
            name=f"ticket-{ctx.author.name}",
            category=category,
            overwrites=self._build_overwrites(guild, ctx.author),
        )
        await channel.send(f"Тикет от {ctx.author.mention}. Описание: {reason or 'Не указано'}")
        await ctx.send(f"Твой тикет создан: {channel.mention}")
        await log_event("ticket_open", f"{ctx.author.id}|{channel.id}")

    @commands.command(name="close_ticket", description="Закрыть тикет.")
    @commands.has_permissions(manage_channels=True)
    async def close_ticket(self, ctx: commands.Context, channel: disnake.TextChannel | None = None) -> None:
        close_channel = channel or ctx.channel
        if not isinstance(close_channel, disnake.TextChannel):
            await ctx.send("❌ Закрывать можно только текстовые каналы.")
            return

        await close_channel.send("Тикет закрыт. Через 10 секунд канал будет удалён.")
        await asyncio.sleep(10)
        await close_channel.delete()
        await log_event("ticket_close", str(close_channel.id))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Tickets(bot))
