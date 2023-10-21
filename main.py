import asyncio
import logging
import os

import aiohttp
import dotenv

from bot import IITMBot, log_setup


async def main():
    with log_setup():
        logger = logging.getLogger("Startbot")
        dotenv.load_dotenv()
        bot = IITMBot._use_default(session=aiohttp.ClientSession())
        logger.info("Loaded instructions")
        token = os.environ["DISCORD_BOT_TOKEN"]
        async with bot:
            await bot.start(token, reconnect=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
