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
MOD_LOG_CHANNEL_ID = int(os.getenv("LOG_CH_MOD", 0))

class TicketModal(disnake.ui.Modal):
    def __init__(self):
        # Компоненты модального окна добавляются в super().__init__()
        components = [
            disnake.ui.TextInput(
                label="Причина обращения",
                style=disnake.TextInputStyle.paragraph,
                placeholder="Опишите проблему или вопрос...",
                custom_id="ticket_reason",
                required=True,
                max_length=1000
            )
        ]
        super().__init__(title="Создание тикета", components=components)

    # Функция, вызываемая после отправки формы
    async def callback(self, interaction: disnake.ModalInteraction):
        # Отправляем "бот печатает" сразу, чтобы избежать тайм-аута в 3 секунды
        await interaction.response.defer()

        # Достаём значение из поля ввода
        reason = interaction.text_values.get("ticket_reason", "Не указана")
        guild = interaction.guild
        author = interaction.user

        # --- ВАШ КОД ДЛЯ СОЗДАНИЯ КАНАЛА ---
        # (оставьте его без изменений)
        category = disnake.utils.get(guild.categories, name=TICKET_CATEGORY)
        if not category:
            category = await guild.create_category(TICKET_CATEGORY)

        overwrites = {
            guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            author: disnake.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True, embed_links=True)
        }
        for role_name in STAFF_ROLE_NAMES:
            role = disnake.utils.get(guild.roles, name=role_name)
            if role:
                overwrites[role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)

        channel_name = f"ticket-{author.name}"
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason=f"Тикет от {author}"
        )

        # Приветственное сообщение в канале
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

        if MOD_LOG_CHANNEL_ID:
            log_channel = interaction.bot.get_channel(MOD_LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(embed=log_embed)

        # Финальное уведомление пользователю
        await interaction.edit_original_response(content=f"✅ Тикет создан: {channel.mention}")
        await log_event("ticket_open", f"{author.id}|{channel.id}|{reason}")

class CloseTicketButton(disnake.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @disnake.ui.button(label="🔒 Закрыть тикет", style=disnake.ButtonStyle.danger, custom_id="close_ticket")
    async def close_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        # ... (код кнопки закрытия оставьте как есть) ...

        # ВАЖНО: добавьте в начало этой функции `await inter.response.defer()`
        if inter.channel.id != self.channel_id:
            await inter.response.send_message("❌ Эта кнопка работает только в соответствующем тикет-канале.", ephemeral=True)
            return
        await inter.response.defer()  # <-- ЭТА СТРОКА
        # ... (остальной код для закрытия) ...

class Tickets(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(
        name="setup_tickets",
        description="Отправить embed с кнопкой для создания тикетов в текущий канал"
    )
    @commands.has_permissions(administrator=True)
    async def setup_tickets(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="🎫 Система тикетов",
            description="Нажмите на кнопку ниже, чтобы создать тикет. Укажите причину обращения, и мы свяжемся с вами.",
            color=disnake.Color.blurple()
        )
        view = CreateTicketView()
        await inter.response.send_message(embed=embed, view=view)

class CreateTicketView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="🎫 Создать тикет", style=disnake.ButtonStyle.primary, custom_id="create_ticket")
    async def create_button(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        # Отправляем модальное окно
        await inter.response.send_modal(TicketModal())

def setup(bot: commands.InteractionBot):
    bot.add_cog(Tickets(bot))