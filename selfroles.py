import disnake
from disnake.ext import commands

# Отдельные маппинги для каждого сообщения
PING_ROLES = {
    '📰': '📰 Новости',
    '📈': '📣 Бамп',
    '🎉': '🎉 Ивенты'
}

COLOR_ROLES = {
    '🟦': 'Голубой',
    '🟨': 'Золотой',
    '🟩': 'Мятный',
    '🟧': 'Оранжевый',
    '🟫': 'Кофейный',
    '⬜': 'Белый'
}

INTEREST_ROLES = {
    '🎨': '🖌️ Художник',
    '💻': '💻 Программист',
    '🎮': '🎮 Геймер'
}

class SelfRoles(commands.Cog):
    def __init__(self, bot): # type: ignore
        self.bot = bot

    @commands.command(
        name='setup_roles',
        description="Установить выбор ролей."
    )
    @commands.has_permissions(manage_roles=True)
    async def setup_roles(self, ctx): # type: ignore
        # Удаляем команду, чтобы не засорять чат
        await ctx.message.delete() # type: ignore

        # 1. Сообщение с пинг-ролями
        ping_embed = disnake.Embed(
            title="Выбери пинг роли",
            description=(
                "Эти роли нужны, чтобы не пропустить всё самое важное и интересное в нашем городке.\n\n"
                "Здесь только твой выбор, можешь выбрать все или только одну."
            ),
            color=0x6A0DAD
        )
        ping_msg = await ctx.send(embed=ping_embed) # type: ignore
        for emoji in PING_ROLES.keys():
            await ping_msg.add_reaction(emoji) # type: ignore

        # 2. Сообщение с цветными ролями
        color_embed = disnake.Embed(
            title="Привет, пушистики и жители нашего городка 🐾",
            description=(
                "Мы добавили набор ролей, чтобы сделать ваш профиль еще уникальнее:\n\n"
                "Чтобы получить роль, просто нажмите на соответствующую реакцию под этим сообщением. "
                "Вы можете выбрать, что нравится вам больше всего.\n\n"
                "Если передумал, то убери и выбери снова."
            ),
            color=0x6A0DAD
        )
        color_msg = await ctx.send(embed=color_embed) # type: ignore
        for emoji in COLOR_ROLES.keys():
            await color_msg.add_reaction(emoji) # pyright: ignore[reportUnknownMemberType]

        # 3. Сообщение с ролями по интересам
        interest_embed = disnake.Embed(
            title="Что насчёт твоих интересов?",
            description=(
                "Мы узнаем что тебе интересно, и сможем подобрать события и мероприятия для тебя.\n\n"
                "Также это поможет найти единомышленников и обсуждать любимые темы вместе.\n\n"
                "Список будет пополняться 🔥"
            ),
            color=0x6A0DAD
        )
        interest_msg = await ctx.send(embed=interest_embed) # type: ignore
        for emoji in INTEREST_ROLES.keys():
            await interest_msg.add_reaction(emoji) # type: ignore

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload): # type: ignore
        if payload.user_id == self.bot.user.id: # type: ignore
            return

        guild = self.bot.get_guild(payload.guild_id) # type: ignore
        if not guild:
            return
        member = guild.get_member(payload.user_id) # type: ignore
        if not member:
            return

        # Объединяем все маппинги для обработки реакций
        ALL_ROLES = {**PING_ROLES, **COLOR_ROLES, **INTEREST_ROLES}
        emoji = str(payload.emoji) # type: ignore
        role_name = ALL_ROLES.get(emoji)

        if role_name:
            role = disnake.utils.get(guild.roles, name=role_name) # type: ignore
            if role:
                await member.add_roles(role) # type: ignore

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload): # type: ignore
        if payload.user_id == self.bot.user.id: # type: ignore
            return

        guild = self.bot.get_guild(payload.guild_id) # type: ignore
        if not guild:
            return
        member = guild.get_member(payload.user_id) # type: ignore
        if not member:
            return

        ALL_ROLES = {**PING_ROLES, **COLOR_ROLES, **INTEREST_ROLES}
        emoji = str(payload.emoji) # type: ignore
        role_name = ALL_ROLES.get(emoji)

        if role_name:
            role = disnake.utils.get(guild.roles, name=role_name) # type: ignore
            if role:
                await member.remove_roles(role) # type: ignore

def setup(bot): # type: ignore
    bot.add_cog(SelfRoles(bot)) # type: ignore