import asyncio
import os
import config
import dotenv

import logging
from logging.handlers import TimedRotatingFileHandler

import discord
from discord.ext import commands
from discord import app_commands 

from contextlib import contextmanager, suppress

logger = logging.getLogger("Bot")

@contextmanager
def log_setup():
    """
    Context manager that sets up file logging
    """
    try:
        dotenv.load_dotenv()
        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.INFO)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        dtfmt = "%Y-%m-%d %H:%M:%S"
        if not os.path.isdir("logs/"):
            os.mkdir("logs/")

        # Add custom logging handlers like rich, maybe in the future??
        handlers = [
            TimedRotatingFileHandler(filename="logs/bot.log", when="d", interval=5),
        ]

        fmt = logging.Formatter(
            "[{asctime}] [{levelname:<7}] {name}: {message}", dtfmt, style="{"
        )

        for handler in handlers:
            if isinstance(handler, TimedRotatingFileHandler):
                handler.setFormatter(fmt)
            logger.addHandler(handler)

        yield
    finally:
        handlers = logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)


class IITMBot(commands.AutoShardedBot):
    """
    Main bot. invoked in runner (main.py) 
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    @classmethod
    def _use_default(cls, *args):
        """
        Create an instance of IITMBot with base configuration
        """

        intents = discord.Intents.all()
        activity = discord.Activity(
            type=discord.ActivityType.watching, name=config.DEFAULT_ACTIVITY_TEXT
        )

        x = cls(
            commands_prefix=config.BOT_PREFIX,
            intents=intents,
            activity=activity
        )
        return x


    async def load_extensions(self, *args):
        for filename in os.listdir("cogs/"):
            if filename.endswith(".py"):
                logger.info(f"Tring to load cogs.{filename[:-3]}")
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                except Exception as e:
                    logger.exception(f"cogs.{filename[:-3]} failed to load: {e}")

    async def close(self):
        """
        Clean exit from discord and aiohttps sessions (maybe for bottle in future?)
        """
        for ext in list(self.extensions):
            with suppress(Exception):
                await self.unload_extension(ext)

        for cog in list(self.cogs):
            with suppress(Exception):
                await self.remove_cog(cog)

        await super().close()

    async def on_ready(self):
        logger.info("Logged in as")
        logger.info(f"\tUser: {self.user.name}")
        logger.info(f"\tID  : {self.user.id}")
        logger.info("------")
