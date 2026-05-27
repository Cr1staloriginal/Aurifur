import disnake
from disnake.ext import commands
import asyncio
from database import log_event

TICKET_CATEGORY = 'Тикеты'
STAFF_ROLE_NAMES = ['🦊 Хвостик порядка', '🦊 Старший хвостик', '🐾 Младшая лапка', '🐾 Старшая лапка', '🐾 Главная лапка']

class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="ticket", description="Создать тикет.")
    async def ticket(self, ctx: commands.Context, *, reason: str | None = None):
        guild = ctx.guild
        if not guild:
            await ctx.send("❌ Только на сервере.")
            return

        category = disnake.utils.get(guild.categories, name=TICKET_CATEGORY)
        if not category:
            category = await guild.create_category(TICKET_CATEGORY)

        overwrites = {
            guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            ctx.author: disnake.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        for role_name in STAFF_ROLE_NAMES:
            role = disnake.utils.get(guild.roles, name=role_name)
            if role:
                overwrites[role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)

        ch = await guild.create_text_channel(f"ticket-{ctx.author.name}", category=category, overwrites=overwrites)
        await ch.send(f"Тикет от {ctx.author.mention}. Причина: {reason or 'Не указана'}")
        await ctx.send(f"✅ Тикет создан: {ch.mention}")

        embed = disnake.Embed(title="🎫 Создан тикет", color=disnake.Color.green(), timestamp=disnake.utils.utcnow())
        embed.add_field(name="Пользователь", value=f"{ctx.author} ({ctx.author.id})", inline=False)
        embed.add_field(name="Канал", value=ch.mention, inline=False)
        embed.add_field(name="Причина", value=reason or "Не указана", inline=False)
        await self.bot.log_dispatcher.send("tickets", embed)

        await log_event('ticket_open', f'{ctx.author.id}|{ch.id}')

    @commands.command(name="close_ticket", description="Закрыть тикет.")
    @commands.has_permissions(manage_channels=True)
    async def close_ticket(self, ctx: commands.Context, channel: disnake.TextChannel | None = None):
        ch = channel or ctx.channel
        await ch.send("⏳ Тикет будет удалён через 10 секунд...")
        embed = disnake.Embed(title="🔒 Закрыт тикет", color=disnake.Color.red(), timestamp=disnake.utils.utcnow())
        embed.add_field(name="Канал", value=ch.mention, inline=False)
        embed.add_field(name="Закрыл", value=ctx.author.mention, inline=False)
        await self.bot.log_dispatcher.send("tickets", embed)

        await asyncio.sleep(10)
        await ch.delete()
        await log_event('ticket_close', f'{ch.id}')

def setup(bot: commands.Bot):
    bot.add_cog(Tickets(bot))