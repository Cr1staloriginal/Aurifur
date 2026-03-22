import discord
from discord import ui
from discord.ext import commands


class AnketaModal(ui.Modal):
    def __init__ (self, submit_channel_id: int):
        super().__init__(title="Отвечай честно и с большим шансом попадёш к нам")
        self.submit_channel_id = submit_channel_id
        self.add_item(ui.TextInput(
            label="Как вы узнали о нашем сервере?*",
            style=discord.TextStyle.short,
            placeholder="Через рекламу, друга, партнёрство и т.д.",
            required=True,
            max_length=1000
        ))
        self.add_item(ui.TextInput(
            label='Что для вас лично означает "фурри-фэндом"?',
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=1000
        ))
        self.add_item(ui.TextInput(
            label="Вас начнут оскорблять в чате, ваши действия?",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        ))
        self.add_item(ui.TextInput(
            label="Есть ли у вас фурсона? Если есть расскажи",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=4000
        ))
        self.add_item(ui.TextInput(
            label="Назовите секретное слово в праилах",
            style=discord.TextStyle.short,
            required=True,
            max_length=500
        ))

    async def on_submit(self, interaction: discord.Interaction):
        answers = [item.value.strip() or "Нет ответа" for item in self.children]

        submit_channel = interaction.client.get_channel(self.submit_channel_id)
        if submit_channel is None:
            await interaction.response.send_message("Ошибка: канал для заявок не найден.", ephemeral=True)
            return

        user = interaction.user

        embed = discord.Embed(
            title="Новая заявка на вступление",
            color=0xffb347,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        embed.set_thumbnail(url=user.display_avatar.url)

        embed.add_field(
            name="Основная информация",
            value=(
                f"Пользователь: {user.mention} | {user}\n"
                f"Аккаунт создан: {user.created_at.strftime('%d.%m.%Y')} "
                f"({discord.utils.format_dt(user.created_at, 'R')})\n"
                f"Присоединился: {discord.utils.format_dt(user.joined_at, 'R') if user.joined_at else 'Не на сервере'}"
            ),
            inline=False
        )

        embed.add_field(name="Ответы на анкету", value="\u200b", inline=False)

        questions = [
            "Как вы узнали о нашем сервере?",
            'Что для вас лично означает "фурри-фэндом"?',
            "Вас начнут оскорблять в чате, ваши действия?",
            "Есть ли у вас фурсона? Если есть расскажи",
            "Назовите самое важное правило сервера"
        ]

        for q, a in zip(questions, answers):
            # Ограничиваем длину поля (максимум 1024 символа)
            value = a[:1000] + "..." if len(a) > 1000 else a
            embed.add_field(name=q, value=value or "—", inline=False)

        await submit_channel.send(embed=embed)
        await interaction.response.send_message(
            "Спасибо! Твоя анкета успешно отправлена модераторам.",
            ephemeral=True
        )


class AnketaView(ui.View):
    def __init__(self, submit_channel_id: int):
        super().__init__(timeout=None)
        self.submit_channel_id = submit_channel_id

    @ui.button(label="Заявка", style=discord.ButtonStyle.blurple, custom_id="anketa:submit_button")
    async def anketa_button(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_modal(AnketaModal(self.submit_channel_id))
        
class AnketaCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # ←←←←← ОБЯЗАТЕЛЬНО ЗАМЕНИ НА РЕАЛЬНЫЙ ID КАНАЛА ←←←←←
        self.submit_channel_id = 1473275301319540840  # !!! ИЗМЕНИ !!!

    @commands.command(name="setup_anketa")
    @commands.has_permissions(administrator=True)
    async def setup_anketa(self, ctx: commands.Context):
        channel = discord.utils.get(ctx.guild.text_channels, name="📝│анкета")
        if not channel:
            await ctx.send("Не найден канал с именем 'анкета' на этом сервере.")
            return

        embed = discord.Embed(
            title="Добро пожаловать на канал 📝│анкета!",
            description=(
                "Нажми кнопку ниже, чтобы заполнить анкету и подать заявку на вступление.\n"
                "Отвечай честно — это сильно повысит шансы!"
            ),
            color=0x00ff88
        )

        view = AnketaView(self.submit_channel_id)
        await channel.send(embed=embed, view=view)
        await ctx.send(f"Готово! Кнопка с анкетой отправлена в {channel.mention}")

    def cog_load(self):
        # Делает persistent кнопку после перезапуска бота
        self.bot.add_view(AnketaView(self.submit_channel_id))


async def setup(bot: commands.Bot):
    await bot.add_cog(AnketaCog(bot))