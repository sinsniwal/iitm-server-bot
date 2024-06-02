from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

import discord
from discord.ext import commands


if TYPE_CHECKING:
    from bot import IITMBot


class Reaction(commands.Cog):
    # Using static variables to store role IDs
    subject_roles = {
        "ds": {
            "Foundational": {
                780958056493744132,  # English 1
                780958551458971668,  # Statistics 1
                780958519846895616,  # Mathematics 1
                780958353492541460,  # Computational Thinking
                780958636515000322,  # Mathematics 2
                780958704181706782,  # Statistics 2
                780958741020278794,  # English 2
                780958774973300746,  # Programming in Python
            },
            "Diploma": {
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
            },
        },
        "es": {
            "Foundational": set(),
            "Diploma": set(),
        },
    }

    roles = {
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
        # ES dont have direct Diploma option
        "dd": {
            "DP": 924703833693749359,  # Diploma Programming
            "DS": 924703232817770497,  # Diploma Science
        },
    }
    Diploma = 780875762277548093
    diploma_alumni = 780879376157376534
    Foundational = 780875583214321684
    foundational_alumni = 780879103237947453
    bsc = 780878697862398002

    def __init__(self, bot: IITMBot):
        self.bot = bot
        self._lock = asyncio.Lock()

    async def send_to_admin(self, message):
        guild = self.bot.guilds[0]
        await guild.get_channel(766072627311673377).send(message)  # type: ignore

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """
        React to a message with a specific emoji to assign or remove roles from a member.
        If the emoji is 🇩, remove all Foundational subject roles from the member and add the roles "Foundational Alumni" and "Diploma".
        If the emoji is 🥋, add the role "Diploma" and the role "Foundational" if the member doesn't have it already.
        If the emoji is 🇧, remove all Foundational and Diploma subject roles, "Foundational" and "Diploma" roles from the member and add the roles "Foundational Alumni", "Diploma Alumni", and "BSc".
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
                if self.roles["ds"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= self.subject_roles["ds"]["Foundational"]
                    # future: subtract bsc or bs roles here
                    new_roles -= {
                        self.roles["ds"]["Foundational"],
                        self.roles["ds"]["Diploma"],
                        self.roles["ds"]["BSc"],
                        self.roles["ds"]["BS"],
                        self.roles["common"]["Foundational"],
                        self.roles["common"]["Diploma"],
                        self.roles["common"]["BSc"],
                        self.roles["common"]["BS"],
                    }
                    new_roles = new_roles.union({self.roles["ds"]["Diploma"], self.roles["common"]["Diploma"]})
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["es"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= self.subject_roles["es"]["Foundational"]
                    # future: subtract bsc or bs roles here
                    new_roles -= {
                        self.roles["es"]["Foundational"],
                        self.roles["es"]["Diploma"],
                        self.roles["es"]["BS"],
                        self.roles["common"]["Foundational"],
                        self.roles["common"]["Diploma"],
                        self.roles["common"]["BSc"],
                        self.roles["common"]["BS"],
                    }
                    new_roles = new_roles.union({self.roles["es"]["Diploma"], self.roles["common"]["Diploma"]})
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["dd"]["DP"] in new_roles or self.roles["dd"]["DS"] in new_roles:
                    await member.send("You cant change your level roles.")
                elif self.roles["common"]["Alum"] in new_roles:
                    await member.send("You cant take Diploma roles if you are an alum.")
                else:
                    await member.send(f"Admins were notified about this error, please wait for them to fix it.")
                    await self.send_to_admin(
                        f"New Role set detected: {new_roles}, user: {member.mention}, userid: {member.id}"
                    )

        elif payload.emoji.name == "🥋":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                if self.roles["ds"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= {
                        self.roles["ds"]["BSc"],
                        self.roles["ds"]["BS"],
                        self.roles["common"]["BSc"],
                        self.roles["common"]["BS"],
                    }
                    new_roles = new_roles.union(
                        {
                            self.roles["ds"]["Foundational"],
                            self.roles["common"]["Foundational"],
                            self.roles["ds"]["Diploma"],
                            self.roles["common"]["Diploma"],
                        }
                    )

                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["es"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= {self.roles["es"]["BS"], self.roles["common"]["BS"]}
                    new_roles = new_roles.union(
                        {
                            self.roles["es"]["Foundational"],
                            self.roles["common"]["Foundational"],
                            self.roles["es"]["Diploma"],
                            self.roles["common"]["Diploma"],
                        }
                    )
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["dd"]["DP"] in new_roles or self.roles["dd"]["DS"] in new_roles:
                    await member.send("You cant change your level roles.")
                elif self.roles["common"]["Alum"] in new_roles:
                    await member.send("You cant take Diploma roles if you are an alum.")
                else:
                    await member.send(f"Admins were notified about this error, please wait for them to fix it.")
                    await self.send_to_admin(
                        f"New Role set detected: {new_roles}, user: {member.mention}, userid: {member.id}"
                    )
        # extra
        elif payload.emoji.name == "🇧":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                if self.roles["ds"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= (
                        self.subject_roles["ds"]["Foundational"]
                        .union(self.subject_roles["ds"]["Diploma"])
                        .union(
                            {
                                self.roles["ds"]["Foundational"],
                                self.roles["ds"]["Diploma"],
                                self.roles["ds"]["BSc"],
                                self.roles["ds"]["BS"],
                                self.roles["common"]["Foundational"],
                                self.roles["common"]["Diploma"],
                                self.roles["common"]["BSc"],
                                self.roles["common"]["BS"],
                            }
                        )
                    )
                    new_roles = new_roles.union({self.roles["ds"]["BSc"], self.roles["common"]["BSc"]})
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["es"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    await member.send("Theres no BSc level in ES")
                elif self.roles["dd"]["DP"] in new_roles or self.roles["dd"]["DS"] in new_roles:
                    await member.send("You cant change your level roles.")
                elif self.roles["common"]["Alum"] in new_roles:
                    if self.roles["ds"]["Alum"] in new_roles:
                        new_roles = new_roles.union({self.roles["common"]["BSc"], self.roles["ds"]["BSc"]})
                        await member.edit(
                            roles=[discord.Object(id=r) for r in new_roles],
                            reason="level change",
                        )
                    elif self.roles["es"]["Alum"] in new_roles:
                        await member.send("Theres no BSc level in ES")
                    else:
                        await member.send(f"Admins were notified about this error, please wait for them to fix it.")
                        await self.send_to_admin(
                            f"New Role set detected: {new_roles}, user: {member.mention}, userid: {member.id}"
                        )

                else:
                    await member.send(f"Admins were notified about this error, please wait for them to fix it.")
                    await self.send_to_admin(
                        f"New Role set detected: {new_roles}, user: {member.mention}, userid: {member.id}"
                    )

        elif payload.emoji.name == "🎓":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                if self.roles["ds"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= (
                        self.subject_roles["ds"]["Foundational"]
                        .union(self.subject_roles["ds"]["Diploma"])
                        .union(
                            {
                                self.roles["ds"]["Foundational"],
                                self.roles["ds"]["Diploma"],
                                self.roles["ds"]["BS"],
                                self.roles["common"]["Foundational"],
                                self.roles["common"]["Diploma"],
                                self.roles["common"]["BS"],
                            }
                        )
                    )
                    new_roles = new_roles.union({self.roles["ds"]["BS"], self.roles["common"]["BS"]})
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["es"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= (
                        self.subject_roles["es"]["Foundational"]
                        .union(self.subject_roles["es"]["Diploma"])
                        .union(
                            {
                                self.roles["es"]["Foundational"],
                                self.roles["es"]["Diploma"],
                                self.roles["es"]["BS"],
                                self.roles["common"]["Foundational"],
                                self.roles["common"]["Diploma"],
                                self.roles["common"]["BS"],
                            }
                        )
                    )
                    new_roles = new_roles.union({self.roles["es"]["BS"], self.roles["common"]["BS"]})
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["dd"]["DP"] in new_roles or self.roles["dd"]["DS"] in new_roles:
                    await member.send("You cant change your level roles.")
                elif self.roles["common"]["Alum"] in new_roles:
                    if self.roles["ds"]["Alum"] in new_roles:
                        new_roles = new_roles.union({self.roles["common"]["BS"], self.roles["ds"]["BS"]})
                        await member.edit(
                            roles=[discord.Object(id=r) for r in new_roles],
                            reason="level change",
                        )
                    elif self.roles["es"]["Alum"] in new_roles:
                        new_roles = new_roles.union({self.roles["common"]["BS"], self.roles["es"]["BS"]})
                        await member.edit(
                            roles=[discord.Object(id=r) for r in new_roles],
                            reason="level change",
                        )
                    else:
                        await member.send(f"Admins were notified about this error, please wait for them to fix it.")
                        await self.send_to_admin(
                            f"New Role set detected: {new_roles}, user: {member.mention}, userid: {member.id}"
                        )
                        return

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """
        If the emoji is 🇩 : remove all Diploma subject roles and the roles "Diploma" from the member and give Foundational role if he doesn't have "BSc" role,
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
                if self.roles["ds"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= self.subject_roles["ds"]["Foundational"].union(self.subject_roles["ds"]["Diploma"])
                    # remove all subject roles and level roles
                    new_roles -= {
                        self.roles["ds"]["Foundational"],
                        self.roles["ds"]["Diploma"],
                        self.roles["ds"]["BSc"],
                        self.roles["ds"]["BS"],
                        self.roles["common"]["Foundational"],
                        self.roles["common"]["Diploma"],
                        self.roles["common"]["BSc"],
                        self.roles["common"]["BS"],
                    }
                    new_roles = new_roles.union(
                        {self.roles["ds"]["Foundational"], self.roles["common"]["Foundational"]}
                    )
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["es"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= self.subject_roles["es"]["Foundational"].union(self.subject_roles["es"]["Diploma"])
                    # remove all subject roles and level roles
                    new_roles -= {
                        self.roles["es"]["Foundational"],
                        self.roles["es"]["Diploma"],
                        self.roles["es"]["BS"],
                        self.roles["common"]["Foundational"],
                        self.roles["common"]["Diploma"],
                        self.roles["common"]["BSc"],
                        self.roles["common"]["BS"],
                    }
                    new_roles = new_roles.union(
                        {self.roles["es"]["Foundational"], self.roles["common"]["Foundational"]}
                    )
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["dd"]["DP"] in new_roles or self.roles["dd"]["DS"] in new_roles:
                    await member.send("You cant change your level roles.")
                elif self.roles["common"]["Alum"] in new_roles:
                    await member.send("You cant take Diploma roles if you are an alum.")
                else:
                    await member.send(f"Admins were notified about this error, please wait for them to fix it.")
                    await self.send_to_admin(
                        f"New Role set detected: {new_roles}, user: {member.mention}, userid: {member.id}"
                    )

        elif payload.emoji.name == "🥋":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                if self.roles["ds"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= self.subject_roles["ds"]["Foundational"]
                    new_roles -= {
                        self.roles["ds"]["BSc"],
                        self.roles["ds"]["BS"],
                        self.roles["common"]["BSc"],
                        self.roles["common"]["BS"],
                        self.roles["ds"]["Foundational"],
                        self.roles["common"]["Foundational"],
                    }
                    new_roles = new_roles.union(
                        {
                            self.roles["ds"]["Diploma"],
                            self.roles["common"]["Diploma"],
                        }
                    )

                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["es"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= self.subject_roles["es"]["Foundational"]
                    new_roles -= {
                        self.roles["es"]["BS"],
                        self.roles["common"]["BS"],
                        self.roles["es"]["Foundational"],
                        self.roles["common"]["Foundational"],
                    }
                    new_roles = new_roles.union({self.roles["es"]["Diploma"], self.roles["common"]["Diploma"]})
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["dd"]["DP"] in new_roles or self.roles["dd"]["DS"] in new_roles:
                    await member.send("You cant change your level roles.")
                elif self.roles["common"]["Alum"] in new_roles:
                    await member.send("You cant take Diploma roles if you are an alum.")
                else:
                    await member.send(f"Admins were notified about this error, please wait for them to fix it.")
                    await self.send_to_admin(
                        f"New Role set detected: {new_roles}, user: {member.mention}, userid: {member.id}"
                    )

        elif payload.emoji.name == "🇧":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                if self.roles["ds"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= self.subject_roles["ds"]["Foundational"].union(self.subject_roles["ds"]["Diploma"])
                    new_roles -= {
                        self.roles["ds"]["BSc"],
                        self.roles["ds"]["BS"],
                        self.roles["common"]["BSc"],
                        self.roles["common"]["BS"],
                        self.roles["ds"]["Foundational"],
                        self.roles["common"]["Foundational"],
                        self.roles["ds"]["Diploma"],
                        self.roles["common"]["Diploma"],
                    }
                    new_roles = new_roles.union(
                        {self.roles["ds"]["Foundational"], self.roles["common"]["Foundational"]}
                    )
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["es"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= self.subject_roles["es"]["Foundational"].union(self.subject_roles["es"]["Diploma"])
                    new_roles -= {
                        self.roles["es"]["BS"],
                        self.roles["common"]["BS"],
                        self.roles["es"]["Foundational"],
                        self.roles["common"]["Foundational"],
                        self.roles["es"]["Diploma"],
                        self.roles["common"]["Diploma"],
                    }
                    new_roles = new_roles.union(
                        {self.roles["es"]["Foundational"], self.roles["common"]["Foundational"]}
                    )
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["dd"]["DP"] in new_roles or self.roles["dd"]["DS"] in new_roles:
                    await member.send("You cant change your level roles.")
                elif self.roles["common"]["Alum"] in new_roles:
                    if self.roles["ds"]["Alum"] in new_roles:
                        new_roles -= {self.roles["ds"]["BSc"], self.roles["common"]["BSc"]}
                        await member.edit(
                            roles=[discord.Object(id=r) for r in new_roles],
                            reason="level change",
                        )
                    elif self.roles["es"]["Alum"] in new_roles:
                        await member.send("Theres no BSc level in ES")
                    else:
                        await member.send(f"Admins were notified about this error, please wait for them to fix it.")
                        await self.send_to_admin(
                            f"New Role set detected: {new_roles}, user: {member.mention}, userid: {member.id}"
                        )
                else:
                    await member.send(f"Admins were notified about this error, please wait for them to fix it.")
                    await self.send_to_admin(
                        f"New Role set detected: {new_roles}, user: {member.mention}, userid: {member.id}"
                    )

        elif payload.emoji.name == "🎓":
            async with self._lock:
                new_roles = {r.id for r in member.roles[1:]}
                if self.roles["ds"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= self.subject_roles["ds"]["Foundational"].union(self.subject_roles["ds"]["Diploma"])
                    new_roles -= {
                        self.roles["ds"]["BS"],
                        self.roles["common"]["BS"],
                        self.roles["ds"]["Foundational"],
                        self.roles["common"]["Foundational"],
                        self.roles["ds"]["Diploma"],
                        self.roles["common"]["Diploma"],
                    }
                    new_roles = new_roles.union({self.roles["ds"]["BSc"], self.roles["common"]["BSc"]})
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["es"]["Student"] in new_roles and self.roles["common"]["Alum"] not in new_roles:
                    new_roles -= self.subject_roles["es"]["Foundational"].union(self.subject_roles["es"]["Diploma"])
                    new_roles -= {
                        self.roles["es"]["BS"],
                        self.roles["common"]["BS"],
                        self.roles["es"]["Foundational"],
                        self.roles["common"]["Foundational"],
                        self.roles["es"]["Diploma"],
                        self.roles["common"]["Diploma"],
                    }
                    new_roles = new_roles.union(
                        {self.roles["es"]["Foundational"], self.roles["common"]["Foundational"]}
                    )
                    await member.edit(
                        roles=[discord.Object(id=r) for r in new_roles],
                        reason="level change",
                    )
                elif self.roles["dd"]["DP"] in new_roles or self.roles["dd"]["DS"] in new_roles:
                    await member.send("You cant change your level roles.")
                elif self.roles["common"]["Alum"] in new_roles:
                    if self.roles["ds"]["Alum"] in new_roles:
                        new_roles -= {self.roles["ds"]["BS"], self.roles["common"]["BS"]}
                        await member.edit(
                            roles=[discord.Object(id=r) for r in new_roles],
                            reason="level change",
                        )
                    elif self.roles["es"]["Alum"] in new_roles:
                        new_roles -= {self.roles["es"]["BS"], self.roles["common"]["BS"]}
                        await member.edit(
                            roles=[discord.Object(id=r) for r in new_roles],
                            reason="level change",
                        )
                    else:
                        await member.send(f"Admins were notified about this error, please wait for them to fix it.")
                        await self.send_to_admin(
                            f"New Role set detected: {new_roles}, user: {member.mention}, userid: {member.id}"
                        )
                else:
                    await member.send(f"Admins were notified about this error, please wait for them to fix it.")
                    await self.send_to_admin(
                        f"New Role set detected: {new_roles}, user: {member.mention}, userid: {member.id}"
                    )

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        async with self._lock:
            if before.roles == after.roles:
                return
            before_ids = set([r.id for r in before.roles])
            isVerified = self.roles["common"]["Verified"] in before_ids

            added = set(after.roles) - set(before.roles)
            removed = set(before.roles) - set(after.roles)
            if len(added) > 1:
                return
            if isVerified:
                return

            try:
                added = added.pop()
                if added.id == self.roles["ds"]["Enthusiast"]:
                    await after.add_roles(discord.Object(id=self.roles["ds"]["Qualifier"]))
                elif added.id == self.roles["es"]["Enthusiast"]:
                    await after.add_roles(discord.Object(id=self.roles["es"]["Qualifier"]))
                else:
                    pass
            except:
                pass

            if len(removed) > 1:
                return
            try:
                removed = removed.pop()
                if removed.id == self.roles["ds"]["Enthusiast"]:
                    await after.remove_roles(discord.Object(id=self.roles["ds"]["Qualifier"]))
                elif removed.id == self.roles["es"]["Enthusiast"]:
                    await after.remove_roles(discord.Object(id=self.roles["es"]["Qualifier"]))
                else:
                    pass
            except:
                pass

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        When a member joins, send them a message with the rules and give them the role "Verified".
        """
        try:
            await member.add_roles(discord.Object(self.roles["common"]["Qualifier"]))
        except:
            pass


async def setup(bot: IITMBot):
    await bot.add_cog(Reaction(bot))
