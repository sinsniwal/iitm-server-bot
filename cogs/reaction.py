from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import discord
from discord.ext import commands


if TYPE_CHECKING:
    from bot import IITMBot


class Reaction(commands.Cog):
    def __init__(self, bot: IITMBot):
        self.bot = bot
        self._lock = asyncio.Lock()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        React to a message with a specific emoji to assign or remove roles from a member.
        If the emoji is 🇩, remove all subject roles from the member and add the roles "Foundational Alumni" and "Diploma".
        If the emoji is 🥋, remove the role "Diploma" from the member and add the role "Foundational" if the member doesn't have it already.
        If the emoji is 🇧, remove all subject roles, "Foundational", and "Diploma" from the member and add the roles "Foundational Alumni", "Diploma Alumni", and "BSc".
        """

        # Following the docstring to the letter:
        # first, define constants before I go crazy
        subject_roles = {
            780958056493744132,  # English 1
            780958551458971668,  # Statistics 1
            780958519846895616,  # Mathematics 1
            780958353492541460,  # Computational Thinking
            780958636515000322,  # Mathematics 2
            780958704181706782,  # Statistics 2
            780958741020278794,  # English 2
            780958774973300746,  # Programming in Python
        }
        diploma = 780875762277548093
        diploma_alumni = 780879376157376534
        foundational = 780875583214321684
        foundational_alumni = 780879103237947453
        bsc = 780878697862398002

        if payload.guild_id is None:
            return  # Reaction is on a private message

        if payload.message_id != 878406133306507354:
            return  # not the message we want

        guild = self.bot.guilds[0]
        member = guild.get_member(payload.user_id)
        assert member
        if member.bot:
            return  # ignore bots

        if payload.emoji.name == "🇩":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                new_roles -= set(subject_roles)
                new_roles.discard(780875583214321684)  # Foundational
                new_roles.add(780879103237947453)  # Foundational Alumni
                new_roles.add(diploma)
                await member.edit(roles=[discord.Object(id=r) for r in new_roles], reason="level change")

        elif payload.emoji.name == "🥋":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                new_roles.discard(diploma)
                new_roles.add(foundational)
                await member.edit(roles=[discord.Object(id=r) for r in new_roles], reason="level change")
        # extra
        elif payload.emoji.name == "🇧":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                new_roles -= set(subject_roles)
                new_roles.discard(foundational)
                new_roles.discard(diploma)
                new_roles.add(foundational_alumni)
                new_roles.add(diploma_alumni)
                new_roles.add(bsc)
                await member.edit(roles=[discord.Object(id=r) for r in new_roles], reason="level change")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """
        If the emoji is 🇩, remove all subject roles from the member and add the roles "Foundational Alumni" and "Diploma".
        If the emoji is 🥋, remove the role "Diploma" from the member and add the role "Foundational" if the member doesn't have it already.
        If the emoji is 🇧, remove all subject roles, "Foundational", and "Diploma" from the member and add the roles "Foundational Alumni", "Diploma Alumni", and "BSc".
        """

        # code duplication is my passion
        subject_roles = {
            780958056493744132,  # English 1
            780958551458971668,  # Statistics 1
            780958519846895616,  # Mathematics 1
            780958353492541460,  # Computational Thinking
            780958636515000322,  # Mathematics 2
            780958704181706782,  # Statistics 2
            780958741020278794,  # English 2
            780958774973300746,  # Programming in Python
        }
        diploma = 780875762277548093
        diploma_alumni = 780879376157376534
        foundational = 780875583214321684
        foundational_alumni = 780879103237947453
        bsc = 780878697862398002
        diploma_subject_roles = {
            878370272728723477,  # DBMS
            878370590367559751,  # PDSA
            878370761470017596,  # AppDev 1
            878370822207701012,  # Java
            878370873734758401,  # AppDev 2
            878370936020172920,  # System Commands
            878371173392605294,  # MLF
            878371228417679380,  # BDM
            878371276442452028,  # MLT
            878371318205120512,  # MLP
            878371364745117697,  # BA
            878371417173925939,  # Tools in DS
        }
        if payload.guild_id is None:
            return

        if payload.message_id != 878406133306507354:
            return  # not the message we want

        guild = self.bot.guilds[0]
        member = guild.get_member(payload.user_id)
        assert member
        if payload.emoji.name == "🇩":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                new_roles -= set(subject_roles)
                new_roles -= set(diploma_subject_roles)
                new_roles.add(foundational_alumni)
                new_roles.add(diploma)
                await member.edit(roles=[discord.Object(id=r) for r in new_roles], reason="level change")

        elif payload.emoji.name == "🥋":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                new_roles.discard(diploma)
                new_roles.add(foundational)
                await member.edit(roles=[discord.Object(id=r) for r in new_roles], reason="level change")

        elif payload.emoji.name == "🇧":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                new_roles -= set(subject_roles)
                new_roles -= set(diploma_subject_roles)
                new_roles.discard(foundational)
                new_roles.discard(diploma)
                new_roles.add(foundational_alumni)
                new_roles.add(diploma_alumni)
                new_roles.add(bsc)
                await member.edit(roles=[discord.Object(id=r) for r in new_roles], reason="level change")


async def setup(bot: IITMBot):
    await bot.add_cog(Reaction(bot))
