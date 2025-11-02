import asyncio
import disnake
from disnake.ext import commands
import config  # <- этот config.py

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.slash_command(
    name="привет",
    description="Бот здоровается с вами.",
    guild_ids=[config.GUILD_ID]  # тестовый сервер
)
async def hello(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message(f"Привет, {inter.author.mention}!")

async def main():
    await bot.start(config.DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())

