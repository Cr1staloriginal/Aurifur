import discord
from discord.ext import commands
from database import log_event

LOG_CHANNEL_NAME = 'aurifur-logs'

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send_log(self, guild, embed):
        ch = discord.utils.get(guild.text_channels, name=LOG_CHANNEL_NAME)
        if ch:
            await ch.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        embed = discord.Embed(title='Сообщение удалено', color=0xE74C3C)
        embed.add_field(name='Автор', value=f'{message.author} ({message.author.id})', inline=False)
        embed.add_field(name='Канал', value=message.channel.mention, inline=False)
        embed.add_field(name='Содержание', value=message.content or '—', inline=False)
        await self.send_log(message.guild, embed)
        await log_event('message_delete', f'{message.author.id}|{message.content}')

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        embed = discord.Embed(title='Изменено сообщение', color=0xF39C12)
        embed.add_field(name='Автор', value=f'{before.author} ({before.author.id})', inline=False)
        embed.add_field(name='До', value=before.content or '—', inline=False)
        embed.add_field(name='После', value=after.content or '—', inline=False)
        embed.add_field(name='Канал', value=before.channel.mention, inline=False)
        await self.send_log(before.guild, embed)
        await log_event('message_edit', f'{before.author.id}|{before.content}->{after.content}')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        embed = discord.Embed(title='Пользователь вошёл', color=0x2ECC71)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.add_field(name='Пользователь', value=f'{member} ({member.id})', inline=False)
        embed.add_field(name='Серверный ник', value=member.display_name, inline=False)
        await self.send_log(member.guild, embed)
        await log_event('member_join', f'{member.id}')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        embed = discord.Embed(title='Пользователь вышел', color=0xE67E22)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.add_field(name='Пользователь', value=f'{member} ({member.id})', inline=False)
        await self.send_log(member.guild, embed)
        await log_event('member_remove', f'{member.id}')

async def setup(bot):
    await bot.add_cog(Logs(bot))
