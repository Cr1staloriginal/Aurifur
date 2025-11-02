import discord
from discord.ext import commands
import asyncio
from database import log_event
from config import GUILD_ID

TICKET_CATEGORY = 'tickets'
STAFF_ROLE = 'Moderator'

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ticket')
    async def ticket(self, ctx, *, reason: str = None):
        guild = ctx.guild
        category = discord.utils.get(guild.categories, name=TICKET_CATEGORY)
        if not category:
            category = await guild.create_category(TICKET_CATEGORY)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            discord.utils.get(guild.roles, name=STAFF_ROLE): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ch = await guild.create_text_channel(f'ticket-{ctx.author.name}', category=category, overwrites=overwrites)
        await ch.send(f'Тикет от {ctx.author.mention}. Описание: {reason or "Не указано"}')
        await ctx.send(f'Твой тикет создан: {ch.mention}')
        await log_event('ticket_open', f'{ctx.author.id}|{ch.id}')

    @commands.command(name='close_ticket')
    @commands.has_permissions(manage_channels=True)
    async def close_ticket(self, ctx, channel: discord.TextChannel = None):
        ch = channel or ctx.channel
        await ch.send('Тикет закрыт. Через 10 секунд канал будет удалён.')
        await asyncio.sleep(10)
        await ch.delete()
        await log_event('ticket_close', f'{ch.id}')

async def setup(bot):
    await bot.add_cog(Tickets(bot))
