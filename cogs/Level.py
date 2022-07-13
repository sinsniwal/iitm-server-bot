import discord
from discord.ext import commands



class Level(commands.Cog):

    def __init__(self,client):
        self.client=client

    @commands.Cog.listener()
    async def on_raw_reaction_add(self,payload):
        if payload.guild_id is None:
            return  # Reaction is on a private message

        if payload.message_id==878406133306507354:
            subject_roles=['english1','statistics1','Mathematics1','Computational Thinking',
                            'Mathematics 2','Statistics 2', 'English 2','Programming in Python']

            
            if payload.emoji.name=='🇩':
                
                guild=self.client.guilds[0]
                member = guild.get_member(payload.user_id)
                diploma=discord.utils.get(guild.roles,name='Diploma')
                if diploma in member.roles:
                    return
                for subject_role in subject_roles:
                    role = discord.utils.get(guild.roles, name=subject_role)
                    if role in member.roles:
                        await member.remove_roles(role, reason="level change")
                
                foundational=discord.utils.get(guild.roles,name='Foundational')
                founda_alumni=discord.utils.get(guild.roles,name='Foundational Alumni')
                if founda_alumni not in member.roles:
                    await member.add_roles(founda_alumni)
                if diploma not in member.roles:
                    await member.add_roles(diploma)
                if foundational in member.roles:
                    await member.remove_roles(foundational)

            elif payload.emoji.name=='🥋':
                guild=self.client.guilds[0]
                member = guild.get_member(payload.user_id)
                diploma=discord.utils.get(guild.roles,name='Diploma')
                if diploma in member.roles:
                    foundational=discord.utils.get(guild.roles,name='Foundational')
                    if foundational not in member.roles:
                        await member.add_roles(foundational)
                    return

                founda_alumni=discord.utils.get(guild.roles,name='Foundational Alumni')
                if founda_alumni not in member.roles:
                    await member.add_roles(founda_alumni,diploma)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self,payload):
        if payload.guild_id is None:
            return
            
        if payload.message_id==878406133306507354:
            subject_roles=['DBMS','PDSA','AppDev 1','Java','AppDev 2','System Commands',
                            'MLF','BDM',"MLT","MLP","BA","Tools in DS"]
            if payload.emoji.name=='🇩':
                
                guild=self.client.guilds[0]
                member = guild.get_member(payload.user_id)
                diploma=discord.utils.get(guild.roles,name='Diploma')
                if diploma not in member.roles:
                    return
                for subject_role in subject_roles:
                    role = discord.utils.get(guild.roles, name=subject_role)
                    if role in member.roles:
                        await member.remove_roles(role, reason="level change")
                
                foundational=discord.utils.get(guild.roles,name='Foundational')
                founda_alumni=discord.utils.get(guild.roles,name='Foundational Alumni')
                if founda_alumni in member.roles:
                    await member.remove_roles(founda_alumni)
                if diploma in member.roles:
                    await member.remove_roles(diploma)
                if foundational not in member.roles:
                    await member.add_roles(foundational)

            elif payload.emoji.name=='🥋':
                guild=self.client.guilds[0]
                member = guild.get_member(payload.user_id)
                diploma=discord.utils.get(guild.roles,name='Diploma')
                if diploma not in member.roles:
                    return
                for subject_role in subject_roles:
                    role = discord.utils.get(guild.roles, name=subject_role)
                    if role in member.roles:
                        await member.remove_roles(role, reason="level change")
                
                foundational=discord.utils.get(guild.roles,name='Foundational')
                founda_alumni=discord.utils.get(guild.roles,name='Foundational Alumni')
                if founda_alumni in member.roles:
                    await member.remove_roles(founda_alumni)
                if diploma in member.roles:
                    await member.remove_roles(diploma)
                if foundational not in member.roles:
                    await member.add_roles(foundational)


def setup(client):
    client.add_cog(Level(client))