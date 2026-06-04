import disnake
from disnake.ext import commands
import os

OWNER_ID = int(os.getenv("OWNER_ID", 0))

class HelpCog(commands.Cog):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot

    @commands.slash_command(name="команды", description="📋 Показать список доступных вам команд")
    async def show_commands(self, inter: disnake.ApplicationCommandInteraction):
        """Отображает команды, доступные текущему пользователю"""
        member = inter.author
        try:
            is_owner = member.id == OWNER_ID
        except Exception:
            is_owner = False

        all_commands = getattr(self.bot, 'slash_commands', []) or []
        available_commands = []

        for cmd in all_commands:
            try:
                if getattr(cmd, "hidden", False):
                    continue

                # Проверка на владельца (команды с @commands.is_owner())
                owner_only = False
                for check in getattr(cmd, 'checks', []):
                    if "is_owner" in str(check):
                        owner_only = True
                        break
                if owner_only and not is_owner:
                    continue

                # Проверка прав default_member_permissions
                required_perms = getattr(cmd, 'default_member_permissions', None)
                if required_perms and getattr(required_perms, 'value', 0) != 0:
                    if isinstance(member, disnake.Member):
                        if not member.guild_permissions.value & required_perms.value:
                            continue
                    else:
                        continue

                available_commands.append(cmd)
            except Exception:
                # Пропускаем команды, которые вызывают исключения при проверке
                continue

        available_commands.sort(key=lambda c: getattr(c, 'name', ''))

        embed = disnake.Embed(
            title="📚 Доступные команды",
            description=f"Всего команд: {len(available_commands)}",
            color=disnake.Color.blurple()
        )

        try:
            if len(available_commands) > 25:
                chunks = [available_commands[i:i+25] for i in range(0, len(available_commands), 25)]
                for i, chunk in enumerate(chunks):
                    cmd_list = "\n".join([f"`/{getattr(cmd, 'name', '')}` — {getattr(cmd, 'description', '')}" for cmd in chunk])
                    embed.add_field(name=f"Страница {i+1}", value=cmd_list[:1024], inline=False)
            else:
                cmd_text = "\n".join([f"`/{getattr(cmd, 'name', '')}` — {getattr(cmd, 'description', '')}" for cmd in available_commands])
                embed.description = cmd_text[:4096]

            embed.set_footer(text=f"Запросил: {getattr(member, 'display_name', str(member))}", icon_url=getattr(member, 'display_avatar', None).url if getattr(member, 'display_avatar', None) else None)
            await inter.response.send_message(embed=embed)
        except Exception as e:
            print(f"HelpCog: ошибка при отправке списка команд: {e}")
            try:
                await inter.response.send_message("Произошла ошибка при получении списка команд.", ephemeral=True)
            except Exception:
                pass

    @commands.slash_command(name="помощь", description="❓ Подробная помощь по конкретной команде")
    async def command_help(self, inter: disnake.ApplicationCommandInteraction, команда: str):
        """Показывает описание и параметры команды"""
        cmd = self.bot.get_slash_command(команда)
        if not cmd:
            try:
                await inter.response.send_message(f"Команда `/{команда}` не найдена.", ephemeral=True)
            except Exception:
                pass
            return

        member = inter.author
        try:
            is_owner = member.id == OWNER_ID
        except Exception:
            is_owner = False

        try:
            if not is_owner and getattr(cmd, 'default_member_permissions', None) and getattr(cmd.default_member_permissions, 'value', 0) != 0:
                if isinstance(member, disnake.Member):
                    if not member.guild_permissions.value & cmd.default_member_permissions.value:
                        await inter.response.send_message(f"❌ У вас нет прав для использования команды `/{getattr(cmd,'name','')}`.", ephemeral=True)
                        return
                else:
                    await inter.response.send_message(f"❌ Команда `/{getattr(cmd,'name','')}` недоступна в личных сообщениях.", ephemeral=True)
                    return

            embed = disnake.Embed(
                title=f"/{getattr(cmd,'name','')}",
                description=getattr(cmd, 'description', None) or "Нет описания",
                color=disnake.Color.green()
            )
            if getattr(cmd, 'options', None):
                params = []
                for opt in cmd.options:
                    required = "обязательный" if getattr(opt, 'required', False) else "опциональный"
                    params.append(f"`{getattr(opt,'name','')}`: {getattr(opt,'description','')} ({required})")
                embed.add_field(name="Параметры", value="\n".join(params), inline=False)

            await inter.response.send_message(embed=embed)
        except Exception as e:
            print(f"HelpCog: ошибка при выводе помощи по команде: {e}")
            try:
                await inter.response.send_message("Произошла ошибка при получении помощи по этой команде.", ephemeral=True)
            except Exception:
                pass

def setup(bot: commands.InteractionBot):
    bot.add_cog(HelpCog(bot))
