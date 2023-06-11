from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import config
import discord
from discord.ext import commands

from utils.helper import admin_only, verification_embed_dm

if TYPE_CHECKING:
    from bot import IITMBot

class Menu(discord.ui.View):
    """
    A Discord UI view that displays a menu for EMAIL VERIFCATION.
    """
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='Verify', custom_id='verify_oauth', style=discord.ButtonStyle.blurple)
    async def verify(self, interaction: discord.Interaction[IITMBot], button: discord.ui.Button) -> None:
        url = await interaction.client.oauth.url_for(interaction.user.id)
        embed = discord.Embed(title='Verify your email address', description=f'Click [here]({url}) to verify your email address. You will be redirected to Google to sign in and verify your email address. Once you have verified your email address, you will be automatically verified in the server.', color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=True)


class Verification(commands.Cog):

    def __init__(self,bot) -> None:
        self.bot = bot
        self._roles = {
            'f': 780875583214321684, # Foundational
            'dp': 924703833693749359, # Diploma Programming
            'ds': 924703232817770497,  # Diploma Science
            '_': 780935056540827729 # Qualifier
        }
    
    @property
    def guild(self) -> discord.Guild:
        return self.bot.get_guild(762774569827565569)


    @commands.command()
    @admin_only()
    async def create(self,ctx):
        await ctx.channel.send("Join our exclusive community and gain access to private channels and premium content by verifying your email address. Click the button below to complete the process and unlock all the benefits of being a part of our server.", view=Menu())
    
    @commands.command()
    @admin_only()
    async def send(self, ctx):
        embed=verification_embed_dm()
        await ctx.author.send(embed=embed)
    
    async def nuke_existing_user(self, user_id: int) -> None:
        mem = self.guild.get_member(user_id)
        if mem:
            await mem.edit(roles=[discord.Object(self._roles['_'])])
    
    async def verify(self, user_id: int, course: str) -> None:
        user = self.guild.get_member(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found in the server, but successfully verified???")
        try:
            role = self._roles[course]
        except KeyError:
            return
        await user.edit(roles=[discord.Object(role)])

async def setup(bot):
    await bot.add_cog(Verification(bot))
