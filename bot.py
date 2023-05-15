import io
import os
from traceback import TracebackException
import config
import dotenv
import sys

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
            logging.StreamHandler(sys.stdout)
        ]

        fmt = logging.Formatter(
            "[{asctime}] [{levelname:<7}] {name}: {message}", dtfmt, style="{"
        )

        for handler in handlers:
            handler.setFormatter(fmt)
            logger.addHandler(handler)

        yield
    finally:
        handlers = logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)

class BotTree(app_commands.CommandTree):
    """
    Subclass of app_commands.CommandTree to define the behavior for the bot's slash command tree.
    Handles thrown errors within the tree and interactions between all commands
    """

    async def log_to_channel(self, interaction: discord.Interaction, err: Exception):
        """
        Log error to discord channel defined in config.py
        """

        channel = await interaction.client.fetch_channel(config.DEV_LOGS_CHANNEL)
        traceback_txt = "".join(TracebackException.from_exception(err).format())
        file = discord.File(
            io.BytesIO(traceback_txt.encode()),
            filename=f"{type(err)}.txt"
        )

        embed = discord.Embed(
            title="Unhandled Exception Alert",
            description=f"""
            Invoked Channel: {interaction.channel.name} 
            \nInvoked User: {interaction.user.display_name} 
            \n```{traceback_txt[2000:].strip()}```                 
            """
        )

        await channel.send(embed=embed, file=file)

    async def on_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        """Handles errors thrown within the command tree"""
        try:
            await self.log_to_channel(interaction, error)
        except Exception as e:
            await super().on_error(interaction, e)


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
            command_prefix=config.BOT_PREFIX,
            intents=intents,
            owner_id=config.OWNER_ID,
            activity=activity,
            tree_cls=BotTree
        )
        return x


    async def load_extensions(self, *args):
        for filename in os.listdir("cogs/"):
            if filename.endswith(".py"):
                logger.info(f"Trying to load cogs.{filename[:-3]}")
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    logger.info(f"Loaded cogs.{filename[:-3]}")
                except Exception as e:
                    logger.error(f"cogs.{filename[:-3]} failed to load: {e}")

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
