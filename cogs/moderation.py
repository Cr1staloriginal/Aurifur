import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from config import OWNER_ID

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- Проверка прав ---
    async def interaction_is_mod(self, interaction: discord.Interaction) -> bool:
        """Проверка, является ли пользователь модератором"""
        perms = interaction.user.guild_permissions
        return perms.manage_messages or interaction.user.id == OWNER_ID

    # --- /kick ---
    @app_commands.command(name="kick", description="Выгнать участника с сервера")
    @app_commands.describe(member="Кого кикнуть", reason="Причина кика")
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "не указана"):
        if not await self.interaction_is_mod(interaction):
            return await interaction.response.send_message("🚫 У вас нет прав на использование этой команды.", ephemeral=True)

        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 {member.display_name} был кикнут. Причина: {reason}")

    # --- /ban ---
    @app_commands.command(name="ban", description="Забанить участника")
    @app_commands.describe(member="Кого забанить", reason="Причина бана")
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "не указана"):
        if not await self.interaction_is_mod(interaction):
            return await interaction.response.send_message("🚫 У вас нет прав на использование этой команды.", ephemeral=True)

        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 {member.display_name} был забанен. Причина: {reason}")

    # --- /mute ---
    @app_commands.command(name="mute", description="Выдать мут пользователю")
    @app_commands.describe(member="Кого замутить", minutes="На сколько минут")
    async def mute(self, interaction: discord.Interaction, member: discord.Member, minutes: int = 10):
        if not await self.interaction_is_mod(interaction):
            return await interaction.response.send_message("🚫 У вас нет прав на использование этой команды.", ephemeral=True)

        role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not role:
            role = await interaction.guild.create_role(name="Muted")
            for ch in interaction.guild.channels:
                await ch.set_permissions(role, send_messages=False, speak=False)

        await member.add_roles(role)
        await interaction.response.send_message(f"🔇 {member.display_name} замучен на {minutes} минут.")

        await asyncio.sleep(minutes * 60)
        await member.remove_roles(role)
        try:
            await interaction.followup.send(f"🔊 {member.display_name} размучен.")
        except discord.NotFound:
            pass

    # --- /purge ---
    @app_commands.command(name="purge", description="Удалить несколько последних сообщений")
    @app_commands.describe(amount="Сколько сообщений удалить")
    async def purge(self, interaction: discord.Interaction, amount: int = 10):
        if not await self.interaction_is_mod(interaction):
            return await interaction.response.send_message("🚫 У вас нет прав на использование этой команды.", ephemeral=True)

        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"🧹 Удалено {len(deleted)} сообщений.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
