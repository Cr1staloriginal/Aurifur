import discord
from discord.ext import commands

ROLE_MESSAGE_TITLE = 'Выбери свои роли'
ROLE_MAP = {
    '\U0001F3A8': 'Artist',
    '\U0001F3AE': 'Gamer',
    '\U0001F3AD': 'RPer',
    '\U0001F495': 'Friend'
}

class SelfRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='roles_message')
    @commands.has_permissions(manage_roles=True)
    async def roles_message(self, ctx):
        embed = discord.Embed(title=ROLE_MESSAGE_TITLE, description='Нажми реакцию, чтобы получить роль.', color=0x6A0DAD)
        msg = await ctx.send(embed=embed)
        for emoji in ROLE_MAP.keys():
            await msg.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        emoji = str(reaction.emoji)
        role_name = ROLE_MAP.get(emoji)
        if role_name:
            role = discord.utils.get(user.guild.roles, name=role_name)
            if role:
                await user.add_roles(role)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        if user.bot:
            return
        emoji = str(reaction.emoji)
        role_name = ROLE_MAP.get(emoji)
        if role_name:
            role = discord.utils.get(user.guild.roles, name=role_name)
            if role:
                await user.remove_roles(role)

async def setup(bot):
    await bot.add_cog(SelfRoles(bot))
