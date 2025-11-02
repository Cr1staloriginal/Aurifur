import discord
from discord.ext import commands
import asyncio
from database import log_event
from config import GUILD_ID

VERIFY_ROLE = 'Verified'

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='verify')
    async def verify(self, ctx):
        await ctx.author.send('Привет! Давай пройдём верификацию. Ответь на 3 вопроса.')
        questions = [
            'Как тебя зовут (ник в сообществе)?',
            'Кто твой персонаж (коротко)?',
            'Почему хочешь быть на сервере?'
        ]
        answers = []
        def check(m):
            return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)

        try:
            for q in questions:
                await ctx.author.send(q)
                msg = await self.bot.wait_for('message', check=check, timeout=120)
                answers.append(msg.content)
            guild = self.bot.get_guild(GUILD_ID)
            mod_chan = discord.utils.get(guild.text_channels, name='verification') if guild else None
            if mod_chan:
                embed = discord.Embed(title='Новая заявка на верификацию', color=0x9B59B6)
                embed.add_field(name='Пользователь', value=f'{ctx.author} ({ctx.author.id})', inline=False)
                for i,q in enumerate(questions):
                    embed.add_field(name=q, value=answers[i], inline=False)
                msg = await mod_chan.send(embed=embed)
                await msg.add_reaction('✅')
                await msg.add_reaction('❌')
                await ctx.author.send('Заявка отправлена модераторам. Ожидай результата.')
                await log_event('verification_submitted', f'{ctx.author.id}')
            else:
                await ctx.author.send('Ошибка: мод-канал не найден.')
        except asyncio.TimeoutError:
            await ctx.author.send('Время ожидания истекло. Попробуй /verify снова.')

async def setup(bot):
    await bot.add_cog(Verification(bot))
