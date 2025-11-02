# Aurifur — project skeleton

Files:
- main.py — launcher
- config.py — reads env vars (DISCORD_TOKEN, GUILD_ID, OWNER_ID)
- database.py — async sqlite helpers
- cogs/ — modules: fun, moderation, logs, verification, tickets, automod, selfroles, levels
- data/aurifur.db — sqlite (created on first run)
- assets/ — placeholders for avatar/banner

## Quick start (local)
1. create `.env` in project root:
   DISCORD_TOKEN=your_token
   GUILD_ID=your_guild_id
   OWNER_ID=your_user_id
2. install deps:
   pip install -U discord.py python-dotenv aiosqlite
3. run:
   python main.py

## Notes
- Commands are prefix-style (use `/command`), you can adapt to slash commands later.
- Replace placeholders in assets/ with real images.
- Database path in config.py is `data/aurifur.db`.

Enjoy — Aurifur 🌙
