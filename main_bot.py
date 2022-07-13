import discord, os, tools
from discord.ext import commands
from itertools import cycle
from discord.utils import get


intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '&', intents = intents)

@client.event
async def on_ready():
    newbie = get(client.guilds[0].roles, name='Newbie')
    serverbots=get(client.guilds[0].roles, name='Bots')
    intrested=get(client.guilds[0].roles, name='Interested')
    for i in client.guilds[0].members:
        if serverbots not in i.roles:
            if intrested not in i.roles:
                await i.add_roles(intrested)
                print(i, " given role intrested")
                # await client.add_roles(i,intrested)
            if newbie in i.roles:
                if len(i.roles)>3:
                    await i.remove_roles(newbie)
                    print(i," removed role newbie")

    tools.change_status.start(client)
    tools.ticketclose.start(client)
    tools.change_auth_token.start()
    print("Bot is ready.")


if __name__ == "__main__":
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.load_extension('cogs.'+filename[:-3])


client.run(tools.TOKEN)
