import discord
from discord.ext import commands
import asyncio
from database import log_event
import aiosqlite
from config import DATABASE_PATH

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("INSERT OR IGNORE INTO users (user_id, username, points) VALUES (?, ?, ?)",
                             (message.author.id, str(message.author), 0))
            await db.execute("UPDATE users SET points = points + 1, last_seen = CURRENT_TIMESTAMP WHERE user_id = ?",
                             (message.author.id,))
            await db.commit()

    @commands.command(name='points')
    async def points(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT points FROM users WHERE user_id = ?", (member.id,)) as cur:
                row = await cur.fetchone()
                pts = row[0] if row else 0
                await ctx.send(f'{member.display_name} имеет {pts} пушистых очков!')

    @commands.command(name='top')
    async def top(self, ctx):
        async with aiosqlite.connect(DATABASE_PATH) as db:
            async with db.execute("SELECT username, points FROM users ORDER BY points DESC LIMIT 10") as cur:
                rows = await cur.fetchall()
                txt = '\n'.join(f'{i+1}. {r[0]} — {r[1]}' for i,r in enumerate(rows))
                await ctx.send(f'🏆 Топ по очкам:\n{txt or "пусто"}')

async def setup(bot):
    await bot.add_cog(Levels(bot))
