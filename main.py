import asyncio
import logging
import os

import dotenv

from bot import IITMBot, log_setup


async def main():
    with log_setup():
        logger = logging.getLogger("Startbot")
        dotenv.load_dotenv()
        bot = IITMBot._use_default()
        await bot.load_extensions()
        logger.info("Loaded instructions")
        token = os.environ["DISCORD_BOT_TOKEN"]
        async with bot:
            await bot.start(token, reconnect=True)


if __name__ == "__main__":
    asyncio.run(main())
