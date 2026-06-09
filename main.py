import os
import disnake
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.InteractionBot(intents=intents)

@bot.event
async def on_ready():
    print(f"Бот {bot.user} готов!")

if __name__ == "__main__":
    bot.load_extensions("cogs")  # автоматически загружает все коги из папки cogs
    bot.run(TOKEN)