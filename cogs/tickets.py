import disnake
from disnake.ext import commands
import asyncio
from database import log_event

TICKET_CATEGORY = 'Тикеты'
STAFF_ROLE_NAMES = ['🦊 Хвостик порядка', '🦊 Старший хвостик', '🐾 Младшая лапка', '🐾 Старшая лапка', '🐾 Главная лапка']

class Tickets(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="ticket", description="🎫 Создать тикет")
    async def ticket(self, inter: disnake.ApplicationCommandInteraction, reason: str = None):
        guild = inter.guild
        if not guild:
            await inter.response.send_message("❌ Команда доступна только на сервере.", ephemeral=True)
            return

        try:
            category = disnake.utils.get(guild.categories, name=TICKET_CATEGORY)
            if not category:
                category = await guild.create_category(TICKET_CATEGORY)

            # Используем ID в имени канала для уникальности
            channel_name = f"ticket-{inter.author.id}"

            overwrites = {
                guild.default_role: disnake.PermissionOverwrite(read_messages=False),
                inter.author: disnake.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            for role_name in STAFF_ROLE_NAMES:
                role = disnake.utils.get(guild.roles, name=role_name)
                if role:
                    overwrites[role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)

            ch = await guild.create_text_channel(
                channel_name,
                category=category,
                overwrites=overwrites
            )

            welcome_text = (
                f"📩 Тикет от {inter.author.mention}\n"
                f"📝 Причина: {reason or 'Не указана'}\n"
                "💬 Опишите свою проблему здесь. Персонал ответит как можно скорее."
            )

            try:
                await ch.send(welcome_text)
            except Exception as e:
                print(f"Tickets: не удалось отправить приветственное сообщение в канал {ch.id}: {e}")

            await inter.response.send_message(f"✅ Тикет создан: {ch.mention}", ephemeral=True)

            embed = disnake.Embed(
                title="🎫 Создан тикет",
                color=disnake.Color.green(),
                timestamp=disnake.utils.utcnow()
            )
            embed.add_field(name="Пользователь", value=f"{inter.author} ({inter.author.id})", inline=False)
            embed.add_field(name="Канал", value=ch.mention, inline=False)
            embed.add_field(name="Причина", value=reason or "Не указана", inline=False)

            try:
                await self.bot.log_dispatcher.send("tickets", embed)
            except Exception as e:
                print(f"Tickets: не удалось отправить embed в log_dispatcher: {e}")

            try:
                await log_event('ticket_open', f'{inter.author.id}|{ch.id}')
            except Exception as e:
                print(f"Tickets: не удалось записать событие в БД ticket_open: {e}")

        except Exception as e:
            print(f"Tickets: ошибка при создании тикета: {e}")
            try:
                await inter.response.send_message("❌ Произошла ошибка при создании тикета.", ephemeral=True)
            except Exception:
                pass

    @commands.slash_command(
        name="close_ticket",
        description="🔒 Закрыть текущий тикет",
        default_member_permissions=disnake.Permissions.manage_channels.value
    )
    @commands.has_permissions(manage_channels=True)
    async def close_ticket(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel = None):
        ch = channel or inter.channel
        if not ch.name.startswith("ticket-"):
            await inter.response.send_message("❌ Эта команда работает только в тикет-каналах.", ephemeral=True)
            return

        await inter.response.send_message("⏳ Тикет будет удалён через 10 секунд...", ephemeral=True)
        try:
            await ch.send("🔒 Тикет закрывается. Спасибо за обращение!")
        except Exception as e:
            print(f"Tickets: не удалось отправить сообщение в канал перед удалением {getattr(ch, 'id', ch)}: {e}")

        embed = disnake.Embed(
            title="🔒 Закрыт тикет",
            color=disnake.Color.red(),
            timestamp=disnake.utils.utcnow()
        )
        embed.add_field(name="Канал", value=ch.mention, inline=False)
        embed.add_field(name="Закрыл", value=inter.author.mention, inline=False)
        try:
            await self.bot.log_dispatcher.send("tickets", embed)
        except Exception as e:
            print(f"Tickets: не удалось отправить embed в log_dispatcher при закрытии: {e}")

        await asyncio.sleep(10)
        try:
            await ch.delete()
        except Exception as e:
            print(f"Tickets: не удалось удалить канал {getattr(ch, 'id', ch)}: {e}")
        try:
            await log_event('ticket_close', f'{getattr(ch, "id", "unknown")}')
        except Exception as e:
            print(f"Tickets: не удалось записать событие в БД ticket_close: {e}")

def setup(bot: commands.InteractionBot):
    bot.add_cog(Tickets(bot))
