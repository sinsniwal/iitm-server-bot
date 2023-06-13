from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands


if TYPE_CHECKING:
    from bot import IITMBot


class Reaction(commands.Cog):
    def __init__(self, bot: IITMBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        React to a message with a specific emoji to assign or remove roles from a member.
        If the emoji is 🇩, remove all subject roles from the member and add the roles "Foundational Alumni" and "Diploma".
        If the emoji is 🥋, remove the role "Diploma" from the member and add the role "Foundational" if the member doesn't have it already.
        If the emoji is 🇧, remove all subject roles, "Foundational", and "Diploma" from the member and add the roles "Foundational Alumni", "Diploma Alumni", and "BSc".
        """
        if payload.guild_id is None:
            return  # Reaction is on a private message

        if payload.message_id == 878406133306507354:
            subject_roles = [
                "english1",
                "statistics1",
                "Mathematics1",
                "Computational Thinking",
                "Mathematics 2",
                "Statistics 2",
                "English 2",
                "Programming in Python",
            ]

            if payload.emoji.name == "🇩":
                guild = self.bot.guilds[0]
                member = guild.get_member(payload.user_id)
                if member is None:
                    return
                diploma = discord.utils.get(guild.roles, name="Diploma")
                if diploma is None:
                    return
                if diploma in member.roles:
                    return
                for subject_role in subject_roles:
                    role = discord.utils.get(guild.roles, name=subject_role)
                    if role in member.roles:
                        await member.remove_roles(role, reason="level change")
                foundational = discord.utils.get(guild.roles, name="Foundational")
                founda_alumni = discord.utils.get(guild.roles, name="Foundational Alumni")
                if founda_alumni is None or foundational is None:
                    return
                if founda_alumni not in member.roles:
                    await member.add_roles(founda_alumni)
                if diploma not in member.roles:
                    await member.add_roles(diploma)
                if foundational in member.roles:
                    await member.remove_roles(foundational)

            elif payload.emoji.name == "🥋":
                guild = self.bot.guilds[0]
                member = guild.get_member(payload.user_id)
                if member is None:
                    return
                diploma = discord.utils.get(guild.roles, name="Diploma")
                if diploma is None:
                    return
                if diploma in member.roles:
                    foundational = discord.utils.get(guild.roles, name="Foundational")
                    if foundational is None:
                        return
                    if foundational not in member.roles:
                        await member.add_roles(foundational)
                    return

                founda_alumni = discord.utils.get(guild.roles, name="Foundational Alumni")
                if founda_alumni is None:
                    return
                if founda_alumni not in member.roles:
                    await member.add_roles(founda_alumni, diploma)
            # extra
            elif payload.emoji.name == "🇧":
                guild = self.bot.guilds[0]
                member = guild.get_member(payload.user_id)
                if member is None:
                    return
                bsc = discord.utils.get(guild.roles, name="BSc")
                if bsc is None:
                    return
                if bsc in member.roles:
                    return
                for subject_role in subject_roles:
                    role = discord.utils.get(guild.roles, name=subject_role)
                    if role in member.roles:
                        await member.remove_roles(role, reason="level change")

                foundational = discord.utils.get(guild.roles, name="Foundational")
                founda_alumni = discord.utils.get(guild.roles, name="Foundational Alumni")
                diploma = discord.utils.get(guild.roles, name="Diploma")
                diploma_alumni = discord.utils.get(guild.roles, name="Diploma Alumni")
                if founda_alumni is None or foundational is None or diploma is None or diploma_alumni is None:
                    return
                if founda_alumni not in member.roles:
                    await member.add_roles(founda_alumni)
                if diploma_alumni not in member.roles:
                    await member.add_roles(diploma_alumni)
                if bsc not in member.roles:
                    await member.add_roles(bsc)
                if foundational in member.roles:
                    await member.remove_roles(foundational)
                if diploma in member.roles:
                    await member.remove_roles(diploma)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """
        If the emoji is 🇩, remove all subject roles from the member and add the roles "Foundational Alumni" and "Diploma".
        If the emoji is 🥋, remove the role "Diploma" from the member and add the role "Foundational" if the member doesn't have it already.
        If the emoji is 🇧, remove all subject roles, "Foundational", and "Diploma" from the member and add the roles "Foundational Alumni", "Diploma Alumni", and "BSc".
        """
        if payload.guild_id is None:
            return

        if payload.message_id == 878406133306507354:
            subject_roles = [
                "DBMS",
                "PDSA",
                "AppDev 1",
                "Java",
                "AppDev 2",
                "System Commands",
                "MLF",
                "BDM",
                "MLT",
                "MLP",
                "BA",
                "Tools in DS",
            ]
            if payload.emoji.name == "🇩":
                guild = self.bot.guilds[0]
                member = guild.get_member(payload.user_id)
                if member is None:
                    return
                diploma = discord.utils.get(guild.roles, name="Diploma")
                if diploma is None:
                    return
                if diploma not in member.roles:
                    return
                for subject_role in subject_roles:
                    role = discord.utils.get(guild.roles, name=subject_role)
                    if role in member.roles:
                        await member.remove_roles(role, reason="level change")

                foundational = discord.utils.get(guild.roles, name="Foundational")
                founda_alumni = discord.utils.get(guild.roles, name="Foundational Alumni")
                if foundational is None or founda_alumni is None:
                    return

                diploma_alumni = discord.utils.get(guild.roles, name="Diploma Alumni")
                if diploma_alumni is None:
                    return
                if founda_alumni in member.roles:
                    await member.remove_roles(founda_alumni)
                if diploma in member.roles:
                    await member.remove_roles(diploma)
                if foundational not in member.roles:
                    await member.add_roles(foundational)
                if diploma_alumni not in member.roles:
                    await member.add_roles(diploma_alumni)

            elif payload.emoji.name == "🥋":
                guild = self.bot.guilds[0]
                member = guild.get_member(payload.user_id)
                if member is None:
                    return
                diploma = discord.utils.get(guild.roles, name="Diploma")
                if diploma not in member.roles:
                    return
                for subject_role in subject_roles:
                    role = discord.utils.get(guild.roles, name=subject_role)
                    if role in member.roles:
                        await member.remove_roles(role, reason="level change")

                foundational = discord.utils.get(guild.roles, name="Foundational")
                if foundational is None:
                    return
                founda_alumni = discord.utils.get(guild.roles, name="Foundational Alumni")
                if founda_alumni in member.roles:
                    await member.remove_roles(founda_alumni)
                if diploma in member.roles:
                    await member.remove_roles(diploma)
                if foundational not in member.roles:
                    await member.add_roles(foundational)

            elif payload.emoji.name == "🇧":
                guild = self.bot.guilds[0]
                member = guild.get_member(payload.user_id)
                if member is None:
                    return
                bsc = discord.utils.get(guild.roles, name="BSc")
                diploma = discord.utils.get(guild.roles, name="Diploma")
                if bsc not in member.roles:
                    return
                for subject_role in subject_roles:
                    role = discord.utils.get(guild.roles, name=subject_role)
                    if role in member.roles:
                        await member.remove_roles(role, reason="level change")

                foundational = discord.utils.get(guild.roles, name="Foundational")
                if foundational is None:
                    return
                founda_alumni = discord.utils.get(guild.roles, name="Foundational Alumni")
                diploma_alumni = discord.utils.get(guild.roles, name="Diploma Alumni")
                if founda_alumni in member.roles:
                    await member.remove_roles(founda_alumni)
                if diploma in member.roles:
                    await member.remove_roles(diploma)
                if diploma_alumni in member.roles:
                    await member.remove_roles(diploma_alumni)
                if bsc in member.roles:
                    await member.remove_roles(bsc)
                if foundational not in member.roles:
                    await member.add_roles(foundational)


async def setup(bot: IITMBot):
    await bot.add_cog(Reaction(bot))
