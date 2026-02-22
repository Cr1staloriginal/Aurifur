import disnake
from disnake.ext import commands
import asyncio
from config import GUILD_ID # type: ignore
from database import log_event

TICKET_CATEGORY = 'Тикеты'
STAFF_ROLE = '🦊 Хвостик порядка, 🦊 Старший хвостик, 🐾 Младшая лапка, 🐾 Старшая лапка, 🐾 Главная лапка'


class Tickets(commands.Cog):
    def __init__(self, bot: commands.Bot):  # ИСПРАВЛЕНО: правильное имя __init__
        self.bot = bot

    @commands.command(
        name="ticket",
        description="Создать тикет."
    )
    
    async def ticket(self, ctx: commands.Context, *, reason: str | None = None) -> None:  # type: ignore[reportUnknownParameterType]
        guild = ctx.guild  # type: ignore[reportUnknownMemberType]

        category = disnake.utils.get(guild.categories, name=TICKET_CATEGORY)  # type: ignore[reportUnknownArgumentType]

        if not category:
            category = await guild.create_category(TICKET_CATEGORY)  # type: ignore[reportUnknownMemberType]

        overwrites = { # type: ignore
            guild.default_role: disnake.PermissionOverwrite(read_messages=False), # type: ignore
            disnake.utils.get(guild.roles, name=STAFF_ROLE): disnake.PermissionOverwrite(  # type: ignore[reportUnknownArgumentType]
                read_messages=True, send_messages=True
            ),
            ctx.author: disnake.PermissionOverwrite(read_messages=True, send_messages=True)  # type: ignore[reportUnknownMemberType]
        }

        ch = await guild.create_text_channel(  # type: ignore[reportUnknownMemberType]
            f'ticket-{ctx.author.name}', category=category, overwrites=overwrites # type: ignore
        )
        await ch.send(f'Тикет от {ctx.author.mention}. Описание: {reason or "Не указано"}')  # type: ignore[reportUnknownMemberType]
        await ctx.send(f'Твой тикет создан: {ch.mention}')  # type: ignore[reportUnknownMemberType]
        await log_event('ticket_open', f'{ctx.author.id}|{ch.id}')

    @commands.command(
        name="close_ticket",
        description="Закрыть тикет."
    )
    @commands.has_permissions(manage_channels=True)
    async def close_ticket(
        self,
        ctx: commands.Context, # type: ignore
        channel: disnake.TextChannel | None = None  # type: ignore[reportUnknownParameterType]
    ) -> None:
        ch = channel or ctx.channel  # type: ignore[reportUnknownVariableType]
        await ch.send('Тикет закрыт. Через 10 секунд канал будет удалён.')  # type: ignore[reportUnknownMemberType]
        await asyncio.sleep(10)
        await ch.delete()  # type: ignore[reportUnknownMemberType]
        await log_event('ticket_close', f'{ch.id}')


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Tickets(bot))
