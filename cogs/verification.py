import config
import discord
from discord.ext import commands

from utils.helper import admin_only, verification_embed_dm


class Menu(discord.ui.View):
    """
    A Discord UI view that displays a menu for EMAIL VERIFICATION.
    """
    def __init__(self) -> None:
        """
        Initializes the menu view and adds a 'Verify' button to the view.
        """
        super().__init__()
        self.add_item(discord.ui.Button(
            label="Verify", custom_id='verify_email', style=discord.ButtonStyle.blurple))


class Verification(commands.Cog):

    def __init__(self,bot) -> None:
        self.bot = bot

    @commands.command()
    @admin_only()
    async def create(self,ctx):
        await ctx.channel.send("Join our exclusive community and gain access to private channels and premium content by verifying your email address. Click the button below to complete the process and unlock all the benefits of being a part of our server.", view=Menu())

    @commands.command()
    @admin_only()
    async def send(self, ctx):
        embed=verification_embed_dm()
        await ctx.author.send(embed=embed)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != config.AUTOMATE_CHANNEL:
            return
        # Compare with ID of Webhook used by Webapp to send the msg
        if message.author.id == config.AUTOMATE_WEBHOOK_ID: 
            data = message.content
            await message.delete()

            # Extract the user's ID, Roll number and old username from the message
            user_id, roll, old_user = data.split("|")
            user_id = int(user_id)

            guild = self.bot.get_guild(762774569827565569) # ID of the server
            user = guild.get_member(user_id)
            
            _roles = {
                'f': 780875583214321684, # Foundational
                'p': 924703833693749359, # Diploma Programming
                's': 924703232817770497,  # Diploma Science
                '_': 780935056540827729 # Qualifier
            }
            try:
                role_id = _roles[roll[2]]
            except KeyError:
                # shouldn't happen, but default to Qualifier just in case
                role_id = _roles['_']
            role = guild.get_role(role_id)
            if role:
                await user.edit(roles=[role])

            # If other users using the same email address are present in the server, remove their roles
            if old_user != 'None':
                if old_user != str(user_id):
                    old_user = int(old_user)
                    mem = guild.get_member(old_user)
                    if mem:
                        role = guild.get_role(_roles['_'])
                        if role is None:
                            raise RuntimeError('Qualifier role not found???')
                        await mem.edit(roles=[role])  # Qualifier

            # Send DM to the user
            embed = verification_embed_dm()
            await user.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Verification(bot))
