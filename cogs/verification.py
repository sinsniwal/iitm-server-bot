from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands

import config
from utils.helper import admin_only, verification_embed_dm


if TYPE_CHECKING:
    from _types import Context
    from bot import IITMBot


class Menu(discord.ui.View):
    """
    A Discord UI view that displays a menu for EMAIL VERIFICATION.
    """

    def __init__(self) -> None:
        """
        Initializes the menu view and adds a 'Verify' button to the view.
        """
        super().__init__()
        self.add_item(discord.ui.Button(label="Verify", custom_id="verify_email", style=discord.ButtonStyle.blurple))


class Verification(commands.Cog):
    def __init__(self, bot: IITMBot) -> None:
        self.bot = bot

        self.roles = {
            "common": {
                "Verified": 1161706698080268411,  # Verified
                "Qualifier": 780935056540827729,  # Qualifier
                "Foundational": 780875583214321684,  # Foundational
                "Diploma": 780875762277548093,  # Diploma
                "BSc": 780878697862398002,  # BSc
                "BS": 1113161111081058396,  # BS
                "Alum": 1161740117011071017,
            },
            "ds": {
                "Student": 1129961686917460029,  # DS Students
                "Enthusiast": 1129973626700050522,  # DS Foundational
                "Qualifier": 1161796522044817448,  # DS Qualifier
                "Foundational": 1161203200041422869,  # DS Foundational
                "Diploma": 1161667546282459226,  # DS Diploma
                "BSc": 1161667625600942180,  # DS BSc
                "BS": 1161667744912130098,  # DS BS
                "Alum": 1161740417830748330,
            },
            # ES dont have BSc level
            "es": {
                "Student": 1129961617694674996,  # ES Students
                "Enthusiast": 1129974121531441175,  # ES Foundational
                "Qualifier": 1161796309213257760,  # ES Qualifier
                "Foundational": 1161202924148490290,  # ES Foundational
                "Diploma": 1161704493424054402,  # ES Diploma
                "BS": 1161704256999534692,  # ES BS
                "Alum": 1161740539662696589,
            },
            # ES dont have direct diploma option
            "dd": {
                "DP": 924703833693749359,  # Diploma Programming
                "DS": 924703232817770497,  # Diploma Science
            },
        }
        self.add_roles = {
            "ds": [
                self.roles["ds"]["Students"],
                self.roles["ds"]["Foundational"],
                self.roles["common"]["Foundational"],
                self.roles["common"]["Verified"],
            ],  # DS, ds foundational, common foundational, common verified
            "es": [
                self.roles["es"]["Students"],
                self.roles["es"]["Foundational"],
                self.roles["common"]["Foundational"],
                self.roles["common"]["Verified"],
            ],  # ES, es foundational, common foundational, common verified
            "ddp": [
                self.roles["dd"]["DP"],
                self.roles["common"]["Diploma"],
                self.roles["common"]["Verified"],
            ],  # dp,common diploma,  common verified
            "dds": [
                self.roles["dd"]["DS"],
                self.roles["common"]["Diploma"],
                self.roles["common"]["Verified"],
            ],  # ds, common verified
        }
        self.remove_roles = [
            self.roles["common"]["Qualifier"],
            self.roles["ds"]["Qualifier"],
            self.roles["es"]["Qualifier"],
        ]

    @commands.command()
    @admin_only()
    async def create(self, ctx: Context):
        await ctx.channel.send(
            "Join our exclusive community and gain access to private channels and premium content by verifying your email address. Click the button below to complete the process and unlock all the benefits of being a part of our server.",
            view=Menu(),
        )

    @commands.command()
    @admin_only()
    async def send(self, ctx: Context):
        embed = verification_embed_dm()
        await ctx.author.send(embed=embed)

    async def send_to_admin(self, message):
        guild = self.bot.guilds[0]
        await guild.get_channel(766072627311673377).send(message)  # type: ignore

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id != config.AUTOMATE_CHANNEL:
            return
        # Compare with ID of Webhook used by Webapp to send the msg
        if message.author.id == config.AUTOMATE_WEBHOOK_ID:
            data = message.content
            await message.delete()

            # Extract the user's ID, Email ID and old username from the message
            user_id, email, old_user = data.split("|")
            user_id = int(user_id)

            guild = self.bot.get_guild(762774569827565569)  # ID of the server
            assert guild
            user = guild.get_member(user_id)
            if user is None:
                return

            addRoles = []
            course = email.split("@")[1][:2].lower()
            if course == "ds":
                if email[2] == "f":
                    addRoles.extend(self.add_roles["ds"])
                elif email[3] == "p":
                    addRoles.extend(self.add_roles["ddp"])
                elif email[3] == "s":
                    addRoles.extend(self.add_roles["dds"])
            elif course == "es":
                addRoles.extend(self.add_roles["es"])
            else:
                # send a message to admin with the email format
                # all send email to the user that admins have been notfied
                # this mean that they have introduced new course
                await user.send(
                    "We have been notified about your email format. Please wait for the admins to add your course."
                )
                await self.send_to_admin(
                    f"New course format detected: {email}, user: {user.mention}, userid: {user.id}"
                )
                return
            for role in addRoles:
                await user.add_roles(discord.Object(role))
            for role in self.remove_roles:
                try:
                    await user.remove_roles(discord.Object(role))
                except:
                    pass
            # sacrifice a *little* bit of readability in the name of EAFP
            # also, exception handling is free since 3.11

            # Remove the spam roles
            try:
                await user.remove_roles(discord.Object(1078208692853420073))  # spam
                await user.remove_roles(discord.Object(1078208892296761404))  # dot 3
                await user.remove_roles(discord.Object(1078208973326536724))  # dot 2
                await user.remove_roles(discord.Object(1078208518793994240))  # dot 1
            except:
                pass
            # If other users using the same email address are present in the server, remove their roles
            if old_user != "None":
                if old_user != str(user_id):
                    old_user = int(old_user)
                    mem = guild.get_member(old_user)
                    if mem:
                        await mem.edit(roles=[discord.Object(self.roles["common"]["Qualifier"])])  # Qualifier

            # Send DM to the user
            embed = verification_embed_dm()
            await user.send(embed=embed)


async def setup(bot: IITMBot):
    await bot.add_cog(Verification(bot))
