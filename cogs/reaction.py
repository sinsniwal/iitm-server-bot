from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import discord
from discord.ext import commands


if TYPE_CHECKING:
    from bot import IITMBot


class Reaction(commands.Cog):
    # Using static variables to store role IDs
    foundational_subject_roles = {
        780958056493744132,  # English 1
        780958551458971668,  # Statistics 1
        780958519846895616,  # Mathematics 1
        780958353492541460,  # Computational Thinking
        780958636515000322,  # Mathematics 2
        780958704181706782,  # Statistics 2
        780958741020278794,  # English 2
        780958774973300746,  # Programming in Python
    }
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
        1022158918237048832,  # BDM Project
        1022159156888739984,  # MAD-1 Project
        1022159348874629151,  # MAD-2 Project
        1022159458035580928,  # MLP Project
    }
    diploma = 780875762277548093
    diploma_alumni = 780879376157376534
    foundational = 780875583214321684
    foundational_alumni = 780879103237947453
    bsc = 780878697862398002

    def __init__(self, bot: IITMBot):
        self.bot = bot
        self._lock = asyncio.Lock()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        React to a message with a specific emoji to assign or remove roles from a member.
        If the emoji is 🇩, remove all foundational subject roles from the member and add the roles "Foundational Alumni" and "Diploma".
        If the emoji is 🥋, add the role "Diploma" and the role "Foundational" if the member doesn't have it already.
        If the emoji is 🇧, remove all foundational and diploma subject roles, "Foundational" and "Diploma" roles from the member and add the roles "Foundational Alumni", "Diploma Alumni", and "BSc".
        """

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
                new_roles -= self.foundational_subject_roles
                new_roles.discard(self.foundational)  # Foundational
                new_roles.add(self.foundational_alumni)  # Foundational Alumni
                new_roles.add(self.diploma)
                await member.edit(
                    roles=[discord.Object(id=r) for r in new_roles],
                    reason="level change",
                )

        elif payload.emoji.name == "🥋":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                new_roles.add(self.foundational)
                new_roles.add(self.foundational_alumni)
                new_roles.add(self.diploma)
                await member.edit(
                    roles=[discord.Object(id=r) for r in new_roles],
                    reason="level change",
                )
        # extra
        elif payload.emoji.name == "🇧":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                new_roles -= self.foundational_subject_roles.union(self.diploma_subject_roles)
                new_roles.discard(self.foundational)
                new_roles.discard(self.diploma)
                new_roles.add(self.foundational_alumni)
                new_roles.add(self.diploma_alumni)
                new_roles.add(self.bsc)
                await member.edit(
                    roles=[discord.Object(id=r) for r in new_roles],
                    reason="level change",
                )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """
        If the emoji is 🇩 : remove all diploma subject roles and the roles "Diploma" from the member and give foundational role if he doesn't have "BSc" role,
        -> If he has "BSc" role, keep the "Foundational Alumni" and "Diploma Alumni" roles.

        If the emoji is 🥋 : if they don't have "BSc" role, remove the roles "Diploma" and "Foundational Alumni" from the member and add the role "Foundational".
        -> If they have "BSc" role, keep the roles "Foundational Alumni" and "Diploma Alumni" and remove the roles "Diploma", and "Foundational".

        If the emoji is 🇧, remove "Diploma Alumni" and "BSc" roles and give them "Foundational" role, if they don't have "Diploma Role".
        """

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
                new_roles -= self.diploma_subject_roles
                new_roles.discard(self.diploma)
                if self.bsc not in new_roles:
                    new_roles.discard(self.foundational_alumni)
                    new_roles.add(self.foundational)
                await member.edit(
                    roles=[discord.Object(id=r) for r in new_roles],
                    reason="level change",
                )

        elif payload.emoji.name == "🥋":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                new_roles.difference_update(self.diploma_subject_roles)
                new_roles.discard(self.diploma)
                if self.bsc not in new_roles:
                    new_roles.discard(self.foundational_alumni)
                    new_roles.add(
                        self.foundational
                    )  # Not adding else because member can be doing BSc and Foundational at same time
                await member.edit(
                    roles=[discord.Object(id=r) for r in new_roles],
                    reason="level change",
                )

        elif payload.emoji.name == "🇧":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                new_roles.discard(self.bsc)
                new_roles.discard(self.diploma_alumni)
                if self.diploma not in new_roles:
                    new_roles.add(self.foundational)
                    new_roles.discard(self.foundational_alumni)
                await member.edit(
                    roles=[discord.Object(id=r) for r in new_roles],
                    reason="level change",
                )


async def setup(bot: IITMBot):
    await bot.add_cog(Reaction(bot))
