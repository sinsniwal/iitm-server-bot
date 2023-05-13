import logging
import os, tools, asyncio
import dotenv
from bot import IITMBot, log_setup

# intents = discord.Intents.all()
# client = commands.Bot(command_prefix="!", intents=intents)

# @client.event
# async def on_ready():
#     print(f"Logged in as {client.user} (ID: {client.user.id})")
#     try:
#         synced = await client.tree.sync()
#         print(f"Synced {len(synced)} commands")
#     except app_commands.CommandError as e:
#         print(f"Error syncing commands: {e}")


# async def load_extensions():
#     for filename in os.listdir('./cogs'):
#         if filename.endswith('.py'):
#             await client.load_extension('cogs.'+filename[:-3])

# async def main():
#     async with client:
#         await load_extensions()
#         await client.start(tools.TOKEN)

async def main():
    with log_setup():

        logger = logging.getLogger("Startbot")
        dotenv.load_dotenv()
        bot = IITMBot._use_default()
        await bot.load_extensions()
        logger.info("Loaded instructions")
        token = os.environ.get("DISCORD_BOT_TOKEN")
        async with bot:
            await bot.start(token, reconnect=True)


if __name__ == "__main__":
    asyncio.run(main())