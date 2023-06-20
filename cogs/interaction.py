from __future__ import annotations

import logging
import os
import re
from typing import TYPE_CHECKING

import discord
from cryptography.fernet import Fernet
from discord import ui
from discord.ext import commands

import config
from utils.helper import send_email


if TYPE_CHECKING:
    from bot import IITMBot


logger = logging.getLogger("Email Verification Modal")


class Verification(ui.Modal, title="Verfication Link"):
    """
    A UI modal that prompts the user to enter their IITMadras Roll number and
    sends a verification email containing a unique verification link to the
    user's email address.

    Methods:
        on_submit: Called when the user submits the modal. If the user's Roll
            number is valid, assigns the appropriate roles to the user and sends
            a verification email containing a unique verification link to the
            user's email address.
        on_timeout: Called when the user fails to submit the modal within the
            specified time limit.
        on_error: Called if there is an error while processing the user's
            submission.

    """

    roll = ui.TextInput(label="Enter Roll Number")

    async def on_submit(self, interaction: discord.Interaction):
        """
        Called when the user submits the verification modal.

        If the user's Roll number is valid, assigns the appropriate roles to the
        user and sends a verification email containing a unique verification link
        to the user's email address.
        """
        assert interaction.guild
        assert isinstance(interaction.user, discord.Member)
        logger.info("on_submit")
        # Retrieve the Fernet Key from the config file and create a Fernet cipher
        cipher = Fernet(os.environ["FERNET"])

        logger.info(cipher)

        # Retrieve the user's Roll number from the text input field and the user's ID from the interaction object
        user_roll = self.roll.value.strip()
        user_id = str(interaction.user.id)

        # Combine the user's Roll number and ID and encrypt it using the Fernet cipher
        data = user_roll + "|" + user_id
        data = data.encode()
        enc = cipher.encrypt(data)
        # Check if the Roll number is valid
        # ignore the case of the Roll number and check if it matches the regex pattern using re.LOWERCASE
        if re.fullmatch("[0-9][0-9][a-z]*[0-9]*", user_roll, re.IGNORECASE) and len(user_roll) in [10, 11]:
            # Assign the appropriate roles to the user based on their number of tries.
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

            # Send a verification email containing a unique verification link to the user's email address
            send_email(interaction.user.name, user_roll, enc)

            # Send a message to the user indicating that a verification link has been sent to their email address
            await interaction.response.send_message(
                f"Please check your email inbox for a link that has been sent to your email address, {user_roll}@ds.study.iitm.ac.in.",
                ephemeral=True,
            )
        else:
            # Send a message to the user indicating that their Roll number is invalid
            await interaction.response.send_message(
                f"For the system to process your request, we require you to enter your official IITMadras Roll number.",
                ephemeral=True,
            )

    async def on_timeout(self, interaction: discord.Interaction) -> None:
        """
        Called when the user fails to submit the modal within the specified time limit.
        """
        await interaction.response.send_message(
            "We apologize, but your session has expired. Please try again and ensure that you enter your email within 5 minutes.",
            ephemeral=True,
        )
        return

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: Exception,
    ) -> None:
        """
        Called if there is an error while processing the user's submission.
        """
        await interaction.response.send_message(
            f"We apologize for the inconvenience. Please contact a moderator and inform them about the error you encountered so that we can fix it: {error}",
            ephemeral=True,
        )
        return


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
                        await interaction.response.send_modal(Verification())
                    else:
                        await interaction.response.send_message(
                            "Please check your email for a verification link that was previously sent to you. Click on this link to complete the verification process for your account.",
                            ephemeral=True,
                        )
                else:
                    await interaction.response.send_message(
                        "You are already verified on this server.Please contact the server staff if you have any questions or concerns.",
                        ephemeral=True,
                    )


async def setup(bot: IITMBot):
    await bot.add_cog(Interaction(bot))
