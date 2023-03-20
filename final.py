
import configparser
from discord import ui
config = configparser.ConfigParser()
config.read('../config.ini')
TOKEN = config['BOT']['token']
OPENCAGE=config['BOT']['opencage']
from cryptography.fernet import Fernet
from tools import send_email
import discord
from discord.ext import commands
import re

import math,requests,json
with open("trains.json",'rb') as f:
    trains=json.load(f)['features']
trainIDs={'06008': ['KOLLAM', 'KollamChennai Central SF Special'], '12670': ['CHHAPRA', 'CHHAPRA - CHENNAI CENTRAL Ganga Kaveri Exp'], '12839': ['HOWRAH', 'Howrah Chennai Superfast Mail'], '12968': ['JAIPUR', 'Jaipur-Chennai SF Express'], '17312': ['VASCO DA GAMA', 'VASCO DA GAMA - CHENNAI CENT Exp'], '22688': ['CHANDIGARH', 'Chandigarh Chennai Express'], '12163': ['DADAR', 'DADAR - CHENNAI EGMORE SF Exp'], '12636': ['MADURAI', 'MADURAI - CHENNAI EGMORE Vaigai SF Exp'], '16126': ['JODHPUR', 'JODHPUR - CHENNAI EGMORE Exp']}
def get_location(pincode):
    api_key = OPENCAGE # Replace with your own API key
    url = f"https://api.opencagedata.com/geocode/v1/json?q={pincode},+India&key={api_key}"
    response = requests.get(url)
    data = response.json()
    
    # Check if any results were found
    if len(data["results"]) == 0:
        return f"No results found for {pincode}."

    # Extract the latitude and longitude from the first result
    latitude = float(data["results"][0]["geometry"]["lat"])
    longitude = float(data["results"][0]["geometry"]["lng"])
    return [latitude,longitude]

def calculate_distance(coord1, coord2):
    # Calculate the great-circle distance between two points on the Earth's surface
    lon1, lat1 = coord1
    lon2, lat2 = coord2
    R = 6371  # Earth's radius in km
    dlon = math.radians(lon2 - lon1)
    dlat = math.radians(lat2 - lat1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return distance

class Verification(ui.Modal, title='Verfication Link'):
    roll = ui.TextInput(label='Enter Roll Number')
    async def on_submit(self, interaction: discord.Interaction):
        Key=config['Key']['fernet'].encode()
        cipher=Fernet(Key)
        userRoll=self.roll.value
        userID=str(interaction.user.id)
        data=userRoll+'|'+userID
        data=data.encode()
        enc=cipher.encrypt(data)


        if re.fullmatch('[0-9][0-9][a-z]*[0-9]*',userRoll) and len(userRoll) in [10,11]:

            dotOne=discord.utils.get(interaction.guild.roles, id=1078208692853420073)
            if dotOne in interaction.user.roles:
                dotTwo=discord.utils.get(interaction.guild.roles, id=1078208892296761404)
                if dotTwo in interaction.user.roles:
                    dotThree=discord.utils.get(interaction.guild.roles, id=1078208973326536724)
                    if dotThree in interaction.user.roles:
                        spam=discord.utils.get(interaction.guild.roles, id=1078208518793994240)
                        interaction.user.add_roles(spam)
                    else:
                        await interaction.user.add_roles(dotThree)
                else:
                    await interaction.user.add_roles(dotTwo)
            else:
                await interaction.user.add_roles(dotOne)
            send_email(interaction.user.name,userRoll,enc)
            await interaction.response.send_message(f"Please check your email inbox for a link that has been sent to your email address, {userRoll}@ds.study.iitm.ac.in.",ephemeral=True)
        else:
            await interaction.response.send_message(f"For the system to process your request, we require you to enter your official IITMadras Roll number.",ephemeral=True)

    async def on_timeout(self,interaction: discord.Interaction) -> None:
        await interaction.response.send_message("We apologize, but your session has expired. Please try again and ensure that you enter your email within 5 minutes.",ephemeral=True)
        return
    
    async def on_error(self, interaction: discord.Interaction, error: Exception, ) -> None:
        await interaction.response.send_message("We apologize for the inconvenience. Please contact a moderator and inform them about the error you encountered so that we can fix it.",ephemeral=True)
        return

class TrainModal(ui.Modal, title='Station Locator'):
    pincode = ui.TextInput(label='Enter PinCode')
    async def on_submit(self, interaction: discord.Interaction):
        userpincode=self.pincode.value
        userID=str(interaction.user.id)
        if userpincode.isnumeric() and len(userpincode)==6:
            #get long and lat
            lat,long=get_location(userpincode)
            global trains,trainIDs
            userTrains=[]
            for train in trains:
                for station in trains['geometry']['coordinates']:
                    if calculate_distance(station,[lat,long])<20:
                        userTrains.append(trainIDs[trains['properties']['number']])
            if userTrains:
                pass
                #give them roles
                await interaction.response.send_message(f"You have been successfully assigned {' ,'.join([a[1] for a in userTrains])}",ephemeral=True)

            else:
                await interaction.response.send_message(f"Sorry, we havent covered your area this time, since this is our first try",ephemeral=True)

        else:
            await interaction.response.send_message(f"Please write a six digit numeric value",ephemeral=True)

            # #change the id from that dict
            # dotOne=discord.utils.get(interaction.guild.roles, id=1078208692853420073)
            # if dotOne in interaction.user.roles:
            #     dotTwo=discord.utils.get(interaction.guild.roles, id=1078208892296761404)
            #     if dotTwo in interaction.user.roles:
            #         dotThree=discord.utils.get(interaction.guild.roles, id=1078208973326536724)
            #         if dotThree in interaction.user.roles:
            #             spam=discord.utils.get(interaction.guild.roles, id=1078208518793994240)
            #             interaction.user.add_roles(spam)
            #         else:
            #             await interaction.user.add_roles(dotThree)
            #     else:
            #         await interaction.user.add_roles(dotTwo)
            # else:
            #     await interaction.user.add_roles(dotOne)
    async def on_timeout(self,interaction: discord.Interaction) -> None:
        await interaction.response.send_message("We apologize, but your session has expired. Please try again and ensure that you enter your pincode within 5 minutes.",ephemeral=True)
        return
    
    async def on_error(self, interaction: discord.Interaction, error: Exception, ) -> None:
        await interaction.response.send_message("We apologize for the inconvenience. Please contact a moderator and inform them about the error you encountered so that we can fix it.",ephemeral=True)
        return
    

class Menu(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.add_item(discord.ui.Button(label="Verify",custom_id='verify_email',style=discord.ButtonStyle.blurple))


class TrainMenu(discord.ui.View):
    def __init__(self) -> None:
        super().__init__()
        self.add_item(discord.ui.Button(label="GetTrain",custom_id='get_train',style=discord.ButtonStyle.blurple))


intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_message(message : discord.Message):
    if message.author.id==730762300503490650:
        if message.content[0:7]=='^create':
            await message.channel.send("Join our exclusive community and gain access to private channels and premium content by verifying your email address. Click the button below to complete the process and unlock all the benefits of being a part of our server.", view=Menu())
        if message.content[0:6]=="^train":
            await message.channel.send("Join Train", view=TrainMenu())
    elif message.author.id==1078142811725123594:
        #read it 
        data=message.content
        await message.delete()
        #delete message
        #update roles
        user_id,roll,old_user=data.split("|")
        user_id=int(user_id)
        guild = bot.get_guild(762774569827565569)
        user = guild.get_member(user_id)
        for role in user.roles[1:]:
            await user.remove_roles(role)
        if roll[2]=='f':
            Foundational=780875583214321684
            role=discord.utils.get(guild.roles, id=Foundational)
            await user.add_roles(role)#Foundational
        elif roll[3]=='p':
            Programming=924703833693749359
            role=discord.utils.get(guild.roles, id=Programming)
            await user.add_roles(role)#Diploma Programming
        elif roll[3]=='s':
            Science=924703232817770497
            role=discord.utils.get(guild.roles, id=Science)
            await user.add_roles(role)# Diploma Science
        if old_user!='None':
            if old_user!=str(user_id):
                old_user=int(old_user)
                Qualifier=780935056540827729
                Qualifier=discord.utils.get(guild.roles, id=Qualifier)
                mem=guild.get_member(old_user)
                if mem:
                    for role in mem.roles[1:]:
                        await mem.remove_roles(role)
                    await mem.add_roles(Qualifier) #Qualifier
@bot.event
async def on_interaction(interaction:discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data["custom_id"] == "verify_email":
            Qualifier=discord.utils.get(interaction.guild.roles, id=780935056540827729)
            spam=discord.utils.get(interaction.guild.roles, id=1078208518793994240)
            if Qualifier in interaction.user.roles:
                if spam not in interaction.user.roles:
                    await interaction.response.send_modal(Verification())
                else:
                    await interaction.response.send_message("Please check your email for a verification link that was previously sent to you. Click on this link to complete the verification process for your account.",ephemeral=True)
            else:
                await interaction.response.send_message("You are already verified on this server.Please contact the server staff if you have any questions or concerns.",ephemeral=True)

    if interaction.type == discord.InteractionType.component:
        if interaction.data["custom_id"] == "get_train":
            await interaction.response.send_modal(TrainModal())

bot.run(TOKEN)
