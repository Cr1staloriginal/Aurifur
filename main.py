async def main():
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not set. Check settings.py or .env.")
        exit(1)

    load_cogs_sync()
    
    try:
        await bot.start(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped manually")
        await bot.close()
    except Exception as e:
        logger.exception("Bot exited with an exception: %s", e)
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
