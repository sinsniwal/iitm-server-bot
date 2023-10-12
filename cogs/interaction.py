from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING

import discord
from cryptography.fernet import Fernet
from discord.ext import commands

import config


if TYPE_CHECKING:
    from bot import IITMBot


logger = logging.getLogger("Email Verification Modal")


class Interaction(commands.Cog):
    def __init__(self, bot: IITMBot):
        self.bot = bot
        self.logger = logging.getLogger("Interaction")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """
        Handles user interactions with the bot, specifically those related to verifying email addresses
        """
        if interaction.type == discord.InteractionType.component:
            if interaction.data["custom_id"] == "verify_email":  # type: ignore  # this is going to go away anyway
                assert interaction.guild
                assert isinstance(interaction.user, discord.Member)
                self.logger.info("Interaction, button")
                # Get the required roles for verification and spam prevention
                qualifier = discord.utils.get(interaction.guild.roles, id=config.QUALIFIER_ROLE)
                spam = discord.utils.get(interaction.guild.roles, id=config.SPAM_ROLE)
                # Check if user has already been verified and is not marked as a spammer
                if qualifier in interaction.user.roles:
                    if spam not in interaction.user.roles:
                        cipher = Fernet(os.environ["FERNET"])
                        logger.info(cipher)
                        # Retrieve the user's ID from the interaction object
                        user_id = str(interaction.user.id)
                        timestamp = int(datetime.now().timestamp())
                        # Combine the user's ID and timestamp and encrypt it using the Fernet cipher
                        data = user_id + "|" + str(timestamp)
                        data = data.encode()
                        enc = cipher.encrypt(data)
                        # Check if the Roll number is valid
                        # ignore the case of the Roll number and check if it matches the regex pattern using re.LOWERCASE
                        # Assign the appropriate roles to the user based on their number of tries.
                        baseURL = f"https://sinsniwal.me/discord-iitm/g-oauth-login/{enc.decode()}"
                        dot_one = discord.utils.get(interaction.guild.roles, id=config.DOT_ONE_ROLE)
                        if not dot_one:
                            return
                        if dot_one in interaction.user.roles:
                            dot_two = discord.utils.get(interaction.guild.roles, id=config.DOT_TWO_ROLE)
                            if not dot_two:
                                return
                            if dot_two in interaction.user.roles:
                                dot_three = discord.utils.get(interaction.guild.roles, id=config.DOT_THREE_ROLE)
                                if not dot_three:
                                    return
                                if dot_three in interaction.user.roles:
                                    spam = discord.utils.get(interaction.guild.roles, id=config.SPAM_ROLE)
                                    if not spam:
                                        return
                                    await interaction.user.add_roles(spam)
                                else:
                                    await interaction.user.add_roles(dot_three)
                            else:
                                await interaction.user.add_roles(dot_two)
                        else:
                            await interaction.user.add_roles(dot_one)
                        embed = discord.Embed()
                        embed.description = (
                            f"Do Not Share This Link With Anyone.Click [here]({baseURL}) to verify using google oauth."
                        )
                        await interaction.response.send_message(
                            embed=embed,
                            ephemeral=True,
                        )

                        # f"Do Not Share This Link With Anyone. Click on the link below to complete the verification process for your account. {baseURL}",

                    else:
                        await interaction.response.send_message(
                            "Limit Reached. Please contact the server staff to increase your limit.",
                            ephemeral=True,
                        )
                else:
                    await interaction.response.send_message(
                        "You are already verified on this server.Please contact the server staff if you have any questions or concerns.",
                        ephemeral=True,
                    )


async def setup(bot: IITMBot):
    await bot.add_cog(Interaction(bot))
