from discord.ext import commands
import discord,os, tools, asyncio
from discord import app_commands

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands")
    except app_commands.CommandError as e:
        print(f"Error syncing commands: {e}")


async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.load_extension('cogs.'+filename[:-3])

async def main():
    async with client:
        await load_extensions()
        await client.start(tools.TOKEN)
if __name__ == "__main__":
    asyncio.run(main())