import discord
from discord import app_commands
from discord.ext import commands


class Slash(commands.Cog):
    """
    This Class is for Slash Commands.
    """

    def __init__(self, bot):
        self.bot = bot

    # Help Command (Ephemeral)
    @app_commands.command(name='help', description='Displays list of commands and their usage')
    @app_commands.describe(command="Input Command Name")
    async def help(self, interaction: discord.Interaction, command: str=None):
        """
        Displays list of commands and their usage
        """
        if command=='help':
            output=discord.Embed(title="Help",description="Displays list of commands and their usage",color=0x00ff00)
        elif not command:
            output=discord.Embed(
                title="Help",
                description="""Displays list of commands and their usage
                Help: Displays list of commands and their usage""",
                color=0x00ff00)
        else:
            output=discord.Embed(title="Error",description="Command not found",color=0xff0000)
        await interaction.response.send_message(embed=output, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Slash(bot))
