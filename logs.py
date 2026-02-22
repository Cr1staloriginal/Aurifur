import disnake
from disnake.ext import commands
from typing import Optional
from database import log_event

LOG_CHANNEL_NAME = "🗃️│логи"
class Logs(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    async def send_log(self, guild: Optional[disnake.Guild], embed: disnake.Embed) -> None:
        """Отправляет лог в канал на сервере, если сервер и канал существуют"""
        if guild is None:
            return

        channel: Optional[disnake.TextChannel] = disnake.utils.get(
            guild.text_channels, name=LOG_CHANNEL_NAME
        )
        if channel is None:
            return

        try:
            await channel.send(embed=embed)
        except disnake.HTTPException:
            pass  # Не критично, если не удалось отправить

    @commands.Cog.listener()
    async def on_message_delete(self, message: disnake.Message) -> None:
        if message.author.bot:
            return

        embed = disnake.Embed(
            title="Сообщение удалено",
            color=0xE74C3C,
            timestamp=disnake.utils.utcnow(),
        )
        embed.add_field(name="Автор", value=f"{message.author} ({message.author.id})", inline=False)
        embed.add_field(
            name="Канал",
            value=message.channel.mention if isinstance(message.channel, disnake.TextChannel) else str(message.channel),
            inline=False,
        )
        embed.add_field(name="Содержание", value=message.content or "— (вложения/эмбеды)", inline=False)

        await self.send_log(message.guild, embed)  # Теперь guild: Optional[Guild] — ок
        await log_event("message_delete", f"{message.author.id}|{message.content or 'no content'}")

    @commands.Cog.listener()
    async def on_message_edit(self, before: disnake.Message, after: disnake.Message) -> None:
        if before.author.bot or before.content == after.content:
            return

        embed = disnake.Embed(
            title="Сообщение изменено",
            color=0xF39C12,
            timestamp=disnake.utils.utcnow(),
        )
        embed.add_field(name="Автор", value=f"{before.author} ({before.author.id})", inline=False)
        embed.add_field(name="До", value=before.content or "—", inline=False)
        embed.add_field(name="После", value=after.content or "—", inline=False)
        embed.add_field(
            name="Канал",
            value=before.channel.mention if isinstance(before.channel, disnake.TextChannel) else str(before.channel),
            inline=False,
        )
        embed.add_field(name="Ссылка", value=f"[Перейти к сообщению]({after.jump_url})", inline=False)

        await self.send_log(before.guild, embed)
        await log_event("message_edit", f"{before.author.id}|{before.content or ''}->{after.content or ''}")

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member) -> None:
        embed = disnake.Embed(
            title="Пользователь присоединился",
            color=0x2ECC71,
            timestamp=disnake.utils.utcnow(),
        )
        embed.set_thumbnail(url=str(member.display_avatar.url))  # str() помогает Pylance понять тип
        embed.add_field(name="Пользователь", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Аккаунт создан", value=disnake.utils.format_dt(member.created_at, "R"), inline=False)

        await self.send_log(member.guild, embed)
        await log_event("member_join", str(member.id))

    @commands.Cog.listener()
    async def on_member_remove(self, member: disnake.Member) -> None:
        embed = disnake.Embed(
            title="Пользователь покинул сервер",
            color=0xE67E22,
            timestamp=disnake.utils.utcnow(),
        )
        embed.set_thumbnail(url=str(member.display_avatar.url))
        embed.add_field(name="Пользователь", value=f"{member} ({member.id})", inline=False)

        await self.send_log(member.guild, embed)
        await log_event("member_remove", str(member.id))


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Logs(bot))