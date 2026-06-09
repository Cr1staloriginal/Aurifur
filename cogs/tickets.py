import disnake
from disnake.ext import commands
import asyncio
import os
from database import log_event

TICKET_CATEGORY = "Тикеты"
STAFF_ROLE_NAMES = [
    "🦊 Хвостик порядка",
    "🦊 Старший хвостик",
    "🐾 Младшая лапка",
    "🐾 Старшая лапка",
    "🐾 Главная лапка"
]
MOD_LOG_CHANNEL_ID = int(os.getenv("LOG_CH_TICKETS", 0))


class TicketModal(disnake.ui.Modal):
    def __init__(self):
        super().__init__(title="Создание тикета")
        self.reason_input = disnake.ui.TextInput(
            label="Причина обращения",
            style=disnake.TextInputStyle.paragraph,
            placeholder="Опишите проблему или вопрос...",
            required=True,
            max_length=1000
        )
        self.add_item(self.reason_input)

    async def on_submit(self, interaction: disnake.ModalInteraction):
        reason = self.reason_input.value
        guild = interaction.guild
        author = interaction.user

        # Поиск или создание категории
        category = disnake.utils.get(guild.categories, name=TICKET_CATEGORY)
        if not category:
            category = await guild.create_category(TICKET_CATEGORY)

        # Права доступа
        overwrites = {
            guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            author: disnake.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True)
        }
        # Добавляем роли персонала
        for role_name in STAFF_ROLE_NAMES:
            role = disnake.utils.get(guild.roles, name=role_name)
            if role:
                overwrites[role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)

        # Создание канала
        channel_name = f"ticket-{author.name}"
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason=f"Тикет от {author}"
        )

        # Отправка приветственного сообщения с кнопкой закрытия
        embed = disnake.Embed(
            title="📩 Ваш тикет создан",
            description=f"**Причина:** {reason}\n\nОпишите вашу проблему подробнее. Персонал скоро свяжется с вами.",
            color=disnake.Color.blurple()
        )
        view = CloseTicketButton(channel.id)
        await channel.send(content=author.mention, embed=embed, view=view)

        # Логирование в канал модерации
        log_embed = disnake.Embed(
            title="🎫 Создан тикет",
            color=disnake.Color.green(),
            timestamp=disnake.utils.utcnow()
        )
        log_embed.add_field(name="Пользователь", value=f"{author} ({author.id})", inline=False)
        log_embed.add_field(name="Канал", value=channel.mention, inline=False)
        log_embed.add_field(name="Причина", value=reason, inline=False)
        await self.send_log(interaction, log_embed)

        # Уведомляем пользователя
        await interaction.response.send_message(
            f"✅ Тикет создан: {channel.mention}",
            ephemeral=True
        )
        await log_event("ticket_open", f"{author.id}|{channel.id}|{reason}")

    async def send_log(self, interaction, embed):
        """Отправка лога в канал модерации"""
        if MOD_LOG_CHANNEL_ID:
            channel = interaction.bot.get_channel(MOD_LOG_CHANNEL_ID)
            if channel:
                await channel.send(embed=embed)


class CloseTicketButton(disnake.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @disnake.ui.button(label="🔒 Закрыть тикет", style=disnake.ButtonStyle.danger, custom_id="close_ticket")
    async def close_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        # Проверяем, что кнопка нажата в том же канале
        if inter.channel.id != self.channel_id:
            await inter.response.send_message("❌ Эта кнопка работает только в соответствующем тикет-канале.", ephemeral=True)
            return
        # Определяем, кто может закрыть: создатель или персонал
        guild = inter.guild
        member = inter.author
        # Проверка на роль персонала
        is_staff = any(role.name in STAFF_ROLE_NAMES for role in member.roles)
        # Проверка на создателя (можно сохранить ID создателя при создании канала, но упростим: если участник может писать в канал и имеет права manage_channels? Лучше разрешить персоналу и создателю. Создателя узнаем из истории канала? Сложно. Поэтому разрешим закрывать любому, у кого есть право manage_channels, либо персоналу. Для простоты: персонал или владелец канала (можно проверить по первой записи? не надёжно). Сделаем: только персонал.
        if not is_staff:
            await inter.response.send_message("❌ Только персонал может закрыть тикет.", ephemeral=True)
            return
        await inter.response.send_message("⏳ Тикет будет удалён через 10 секунд...")
        await inter.channel.send("🔒 Тикет закрывается. Спасибо за обращение!")
        # Логирование закрытия
        log_embed = disnake.Embed(
            title="🔒 Закрыт тикет",
            color=disnake.Color.red(),
            timestamp=disnake.utils.utcnow()
        )
        log_embed.add_field(name="Канал", value=inter.channel.mention, inline=False)
        log_embed.add_field(name="Закрыл", value=member.mention, inline=False)
        if MOD_LOG_CHANNEL_ID:
            log_channel = inter.bot.get_channel(MOD_LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(embed=log_embed)
        await asyncio.sleep(10)
        await inter.channel.delete()
        await log_event("ticket_close", f"{inter.channel.id}|closed by {member.id}")


class Tickets(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(
        name="setup_tickets",
        description="Отправить embed с кнопкой для создания тикетов в текущий канал"
    )
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, inter: disnake.ApplicationCommandInteraction):
        """Создаёт embed с кнопкой «Создать тикет» в текущем канале"""
        embed = disnake.Embed(
            title="🎫 Система тикетов",
            description="Нажмите на кнопку ниже, чтобы создать тикет. Укажите причину обращения, и мы свяжемся с вами.",
            color=disnake.Color.blurple()
        )
        view = CreateTicketView()
        await inter.response.send_message(embed=embed, view=view)

    @commands.slash_command(
        name="close_ticket",
        description="Закрыть текущий тикет (альтернативный способ)"
    )
    async def close_ticket(self, inter: disnake.ApplicationCommandInteraction):
        """Закрывает тикет-канал, если пользователь имеет права"""
        if not inter.channel.name.startswith("ticket-"):
            await inter.response.send_message("❌ Эта команда работает только в тикет-каналах.", ephemeral=True)
            return
        # Проверка прав: персонал или создатель (упростим: только персонал)
        is_staff = any(role.name in STAFF_ROLE_NAMES for role in inter.author.roles)
        if not is_staff:
            await inter.response.send_message("❌ Только персонал может закрыть тикет.", ephemeral=True)
            return
        await inter.response.send_message("⏳ Тикет будет удалён через 10 секунд...")
        await inter.channel.send("🔒 Тикет закрывается. Спасибо за обращение!")
        # Логирование
        log_embed = disnake.Embed(
            title="🔒 Закрыт тикет",
            color=disnake.Color.red(),
            timestamp=disnake.utils.utcnow()
        )
        log_embed.add_field(name="Канал", value=inter.channel.mention, inline=False)
        log_embed.add_field(name="Закрыл", value=inter.author.mention, inline=False)
        if MOD_LOG_CHANNEL_ID:
            log_channel = inter.bot.get_channel(MOD_LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(embed=log_embed)
        await asyncio.sleep(10)
        await inter.channel.delete()
        await log_event("ticket_close", f"{inter.channel.id}|closed by {inter.author.id}")


class CreateTicketView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="🎫 Создать тикет", style=disnake.ButtonStyle.primary, custom_id="create_ticket")
    async def create_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_modal(TicketModal())


def setup(bot: commands.InteractionBot):
    bot.add_cog(Tickets(bot))