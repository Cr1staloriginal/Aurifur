import disnake
from disnake import ui
from disnake.ext import commands

class AnketaModal(ui.Modal):
    def __init__(self, submit_channel_id: int):
        super().__init__(title="Отвечай честно и с большим шансом попадёшь к нам")
        self.submit_channel_id = submit_channel_id
        self.add_item(ui.TextInput(
            label="Как вы узнали о нашем сервере?*",
            style=disnake.TextInputStyle.short,
            placeholder="Через рекламу, друга, партнёрство и т.д.",
            required=True,
            max_length=1000
        ))
        self.add_item(ui.TextInput(
            label='Что для вас лично означает "фурри-фэндом"?',
            style=disnake.TextInputStyle.paragraph,
            required=True,
            max_length=1000
        ))
        self.add_item(ui.TextInput(
            label="Вас начнут оскорблять в чате, ваши действия?",
            style=disnake.TextInputStyle.paragraph,
            required=True,
            max_length=500
        ))
        self.add_item(ui.TextInput(
            label="Есть ли у вас фурсона? Если есть расскажи",
            style=disnake.TextInputStyle.paragraph,
            required=True,
            max_length=4000
        ))
        self.add_item(ui.TextInput(
            label="Ознакомились ли вы с правилами сервера?",
            style=disnake.TextInputStyle.short,
            required=True,
            max_length=500
        ))

    async def on_submit(self, interaction: disnake.ModalInteraction):
        answers = [item.value.strip() or "Нет ответа" for item in self.children]
        submit_channel = interaction.bot.get_channel(self.submit_channel_id)
        if not submit_channel:
            await interaction.response.send_message("Ошибка: канал для заявок не найден.", ephemeral=True)
            return
        user = interaction.user
        embed = disnake.Embed(
            title="Новая заявка на вступление",
            color=0xffb347,
            timestamp=disnake.utils.utcnow()
        )
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(
            name="Основная информация",
            value=(
                f"Пользователь: {user.mention} | {user}\n"
                f"Аккаунт создан: {user.created_at.strftime('%d.%m.%Y')} "
                f"({disnake.utils.format_dt(user.created_at, 'R')})\n"
                f"Присоединился: {disnake.utils.format_dt(user.joined_at, 'R') if user.joined_at else 'Не на сервере'}"
            ),
            inline=False
        )
        embed.add_field(name="Ответы на анкету", value="\u200b", inline=False)
        questions = [
            "Как вы узнали о нашем сервере?",
            'Что для вас лично означает "фурри-фэндом"?',
            "Вас начнут оскорблять в чате, ваши действия?",
            "Есть ли у вас фурсона? Если есть расскажи",
            "Ознакомились ли вы с правилами сервера?"
        ]
        for q, a in zip(questions, answers):
            value = a[:1000] + "..." if len(a) > 1000 else a
            embed.add_field(name=q, value=value or "—", inline=False)
        await submit_channel.send(embed=embed)
        await interaction.response.send_message("Спасибо! Анкета отправлена модераторам.", ephemeral=True)

class AnketaView(ui.View):
    def __init__(self, submit_channel_id: int):
        super().__init__(timeout=None)
        self.submit_channel_id = submit_channel_id
    @ui.button(label="Заявка", style=disnake.ButtonStyle.blurple, custom_id="anketa:submit_button")
    async def anketa_button(self, interaction: disnake.MessageInteraction, button: ui.Button):
        await interaction.response.send_modal(AnketaModal(self.submit_channel_id))

class AnketaCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        # ⚠️ ЗАМЕНИТЕ НА РЕАЛЬНЫЙ ID КАНАЛА ДЛЯ ЗАЯВОК
        self.submit_channel_id = 1473275301319540840

    @commands.slash_command(
        name="setup_anketa",
        description="Отправить кнопку для анкеты в канал 📝╔верификация",
        default_member_permissions=disnake.Permissions.administrator.value
    )
    @commands.has_permissions(administrator=True)
    async def setup_anketa(self, inter: disnake.ApplicationCommandInteraction):
        channel = disnake.utils.get(inter.guild.text_channels, name="📝╔верификация")
        if not channel:
            await inter.response.send_message("Не найден канал '📝╔верификация'.", ephemeral=True)
            return
        embed = disnake.Embed(
            title="Добро пожаловать!",
            description="Нажми кнопку, чтобы заполнить анкету.",
            color=0x00ff88
        )
        view = AnketaView(self.submit_channel_id)
        await channel.send(embed=embed, view=view)
        await inter.response.send_message(f"✅ Кнопка отправлена в {channel.mention}", ephemeral=True)

    def cog_load(self):
        self.bot.add_view(AnketaView(self.submit_channel_id))

def setup(bot: commands.InteractionBot):
    bot.add_cog(AnketaCog(bot))
