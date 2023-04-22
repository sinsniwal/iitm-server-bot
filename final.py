import configparser
from discord import ui
from cryptography.fernet import Fernet
from tools import send_email
import discord
from discord.ext import commands
import re
import math
import requests
import json

config = configparser.ConfigParser()
config.read('../config.ini')
TOKEN = config['BOT']['token']
OPENCAGE = config['BOT']['opencage']


class Verification(ui.Modal, title='Verfication Link' ):
    roll = ui.TextInput(label='Enter Roll Number')

    async def on_submit(self, interaction: discord.Interaction):
        Key = config['Key']['fernet'].encode()
        cipher = Fernet(Key)
        userRoll = self.roll.value
        userID = str(interaction.user.id)
        data = userRoll+'|'+userID
        data = data.encode()
        enc = cipher.encrypt(data)

        if re.fullmatch('[0-9][0-9][a-z]*[0-9]*', userRoll) and len(userRoll) in [10, 11]:

            dotOne = discord.utils.get(
                interaction.guild.roles, id=1078208692853420073)
            if dotOne in interaction.user.roles:
                dotTwo = discord.utils.get(
                    interaction.guild.roles, id=1078208892296761404)
                if dotTwo in interaction.user.roles:
                    dotThree = discord.utils.get(
                        interaction.guild.roles, id=1078208973326536724)
                    if dotThree in interaction.user.roles:
                        spam = discord.utils.get(
                            interaction.guild.roles, id=1078208518793994240)
                        interaction.user.add_roles(spam)
                    else:
                        await interaction.user.add_roles(dotThree)
                else:
                    await interaction.user.add_roles(dotTwo)
            else:
                await interaction.user.add_roles(dotOne)
            send_email(interaction.user.name, userRoll, enc)
            await interaction.response.send_message(f"Please check your email inbox for a link that has been sent to your email address, {userRoll}@ds.study.iitm.ac.in.", ephemeral=True)
        else:
            await interaction.response.send_message(f"For the system to process your request, we require you to enter your official IITMadras Roll number.", ephemeral=True)

    async def on_timeout(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("We apologize, but your session has expired. Please try again and ensure that you enter your email within 5 minutes.", ephemeral=True)
        return

    async def on_error(self, interaction: discord.Interaction, error: Exception, ) -> None:
        await interaction.response.send_message("We apologize for the inconvenience. Please contact a moderator and inform them about the error you encountered so that we can fix it.", ephemeral=True)
        return


class Menu(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.add_item(discord.ui.Button(
            label="Verify", custom_id='verify_email', style=discord.ButtonStyle.blurple))


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_message(message: discord.Message):
    if message.author.id == 730762300503490650:
        if message.content[0:7] == '^create':
            await message.channel.send("Join our exclusive community and gain access to private channels and premium content by verifying your email address. Click the button below to complete the process and unlock all the benefits of being a part of our server.", view=Menu())
    elif message.author.id == 1078142811725123594:
        # read it
        data = message.content
        await message.delete()
        # delete message
        # update roles
        user_id, roll, old_user = data.split("|")
        user_id = int(user_id)
        guild = bot.get_guild(762774569827565569)
        user = guild.get_member(user_id)
        for role in user.roles[1:]:
            await user.remove_roles(role)
        if roll[2] == 'f':
            Foundational = 780875583214321684
            role = discord.utils.get(guild.roles, id=Foundational)
            await user.add_roles(role)  # Foundational
        elif roll[3] == 'p':
            Programming = 924703833693749359
            role = discord.utils.get(guild.roles, id=Programming)
            await user.add_roles(role)  # Diploma Programming
        elif roll[3] == 's':
            Science = 924703232817770497
            role = discord.utils.get(guild.roles, id=Science)
            await user.add_roles(role)  # Diploma Science
        if old_user != 'None':
            if old_user != str(user_id):
                old_user = int(old_user)
                Qualifier = 780935056540827729
                Qualifier = discord.utils.get(guild.roles, id=Qualifier)
                mem = guild.get_member(old_user)
                if mem:
                    for role in mem.roles[1:]:
                        await mem.remove_roles(role)
                    await mem.add_roles(Qualifier)  # Qualifier


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data["custom_id"] == "verify_email":
            Qualifier = discord.utils.get(
                interaction.guild.roles, id=780935056540827729)
            spam = discord.utils.get(
                interaction.guild.roles, id=1078208518793994240)
            if Qualifier in interaction.user.roles:
                if spam not in interaction.user.roles:
                    await interaction.response.send_modal(Verification())
                else:
                    await interaction.response.send_message("Please check your email for a verification link that was previously sent to you. Click on this link to complete the verification process for your account.", ephemeral=True)
            else:
                await interaction.response.send_message("You are already verified on this server.Please contact the server staff if you have any questions or concerns.", ephemeral=True)


@bot.event
async def on_raw_reaction_add(payload):
    if payload.guild_id is None:
        return  # Reaction is on a private message

    if payload.message_id==878406133306507354:
        subject_roles=['english1','statistics1','Mathematics1','Computational Thinking',
                        'Mathematics 2','Statistics 2', 'English 2','Programming in Python']
        
        if payload.emoji.name=='🇩':
            
            guild=bot.guilds[0]
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
            guild=bot.guilds[0]
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
#extra
        elif payload.emoji.name=='🇧':
            guild=bot.guilds[0]
            member = guild.get_member(payload.user_id)
            bsc=discord.utils.get(guild.roles,name='BSc')
            if bsc in member.roles:
                return
            for subject_role in subject_roles:
                role = discord.utils.get(guild.roles, name=subject_role)
                if role in member.roles:
                    await member.remove_roles(role, reason="level change")
            
            foundational=discord.utils.get(guild.roles,name='Foundational')
            founda_alumni=discord.utils.get(guild.roles,name='Foundational Alumni')
            diploma=discord.utils.get(guild.roles,name='Diploma')
            diploma_alumni=discord.utils.get(guild.roles,name='Diploma Alumni')
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



@bot.event
async def on_raw_reaction_remove(payload):
    if payload.guild_id is None:
        return
        
    if payload.message_id==878406133306507354:
        subject_roles=['DBMS','PDSA','AppDev 1','Java','AppDev 2','System Commands',
                        'MLF','BDM',"MLT","MLP","BA","Tools in DS"]
        if payload.emoji.name=='🇩':
            
            guild=bot.guilds[0]
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

            diploma_alumni=discord.utils.get(guild.roles,name='Diploma Alumni')
            if founda_alumni in member.roles:
                await member.remove_roles(founda_alumni)
            if diploma in member.roles:
                await member.remove_roles(diploma)
            if foundational not in member.roles:
                await member.add_roles(foundational)
            if diploma_alumni not in member.roles:
                await member.add_roles(diploma_alumni)

        elif payload.emoji.name=='🥋':
            guild=bot.guilds[0]
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

        elif payload.emoji.name=='🇧':
            guild=bot.guilds[0]
            member = guild.get_member(payload.user_id)
            bsc=discord.utils.get(guild.roles,name='BSc')
            diploma=discord.utils.get(guild.roles,name='Diploma')
            if bsc not in member.roles:
                return
            for subject_role in subject_roles:
                role = discord.utils.get(guild.roles, name=subject_role)
                if role in member.roles:
                    await member.remove_roles(role, reason="level change")
            
            foundational=discord.utils.get(guild.roles,name='Foundational')
            founda_alumni=discord.utils.get(guild.roles,name='Foundational Alumni')
            diploma_alumni=discord.utils.get(guild.roles,name='Diploma Alumni')
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




bot.run(TOKEN)
