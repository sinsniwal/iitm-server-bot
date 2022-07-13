import discord, tools, re, random, ast, time
from discord.ext import commands
from discord.utils import get
from tools import otp_info


class Verification(commands.Cog):

    def __init__(self,client):
        self.client=client

    @commands.Cog.listener()
    async def on_message(self,msg):
        main_gate_id=794889866780737536 
        tickettoolid = 557628352828014614
        main_gate_bot=self.client.get_channel(int(main_gate_id))
        try:
            if msg.channel.category.name=="open" and msg.author.id!=main_gate_id:
                try:
                    if msg.author.id == tickettoolid:
                        async for mess in msg.channel.history(limit=1):
                            await mess.delete()
                        embed=tools.create_embed()
                        await msg.channel.send(embed=embed,allowed_mentions=discord.AllowedMentions.all())
                        return
                        
                    elif msg.channel.id not in otp_info:
                        if re.fullmatch('[0-9][0-9][a-z]*[0-9]*@student.onlinedegree.iitm.ac.in',msg.content):
                            await tools.edit_first_message(msg,['emailr'])
                            otp_info[msg.channel.id] = [-100,"0",0,'',0]   
                            counter = 0
                            otp=random.randint(100000000,999999999)
                            email = msg.content
                            level=''
                            userid=msg.author.id
                            if msg.content[2].lower()=='f':
                                level='f'
                            elif  msg.content[2:4].lower()=='ds':
                                level='ds'
                            elif msg.content[2:4].lower()=='dp':
                                level='dp'
                            otp_info[msg.channel.id] = [otp,email,1,level,userid]
                            try:
                                name= await self.client.fetch_user(int(userid))
                                tools.send_email(name.name,otp,email)
                                await msg.delete()
                                # await msg.channel.send(f"Okay, OTP sent at {email}, so check spam and promotions. Please send that OTP here, and you got three attempts.")
                                
                            except:
                                pass 

                            #send email to user
                            #and give them update

                        else:
                            await msg.delete()
                            await tools.edit_first_message(msg,['emailw'])
                            # await tools.edit_first_message(msg,'Please write your IITM official student Email ID! with @student.onlinedegree.iitm.ac.in')
                            # await msg.channel.send("Please write your IITM official student Email ID! with @student.onlinedegree.iitm.ac.in")
                            
                    elif otp_info[msg.channel.id][2]<3:
                        #user input is exact match of otp
                        await msg.delete()
                        if f"{otp_info[msg.channel.id][0]}" == msg.content:
                            await tools.edit_first_message(msg,['otpr'])
                            #search if the email id is already registered, if it is then kick old user.
                            if otp_info[msg.channel.id][3]=='f':
                                await msg.author.add_roles(msg.guild.get_role(780875583214321684))
                            elif otp_info[msg.channel.id][3]=='dp':
                                await msg.author.add_roles(msg.guild.get_role(780875762277548093))
                                await msg.author.add_roles(msg.guild.get_role(924703833693749359))
                            elif otp_info[msg.channel.id][3]=='ds':
                                await msg.author.add_roles(msg.guild.get_role(780875762277548093))
                                await msg.author.add_roles(msg.guild.get_role(924703232817770497))
                            else:
                                a=1/0
                            await tools.edit_first_message(msg,['level',otp_info[msg.channel.id][3].upper()])
                            async with  msg.channel.typing():
                                try:
                                    houserole=get(self.client.guilds[0].roles, id=835238631848804353)
                                    house=tools.get_house(otp_info[msg.channel.id][1])
                                    if house:
                                        await msg.author.add_roles(get(self.client.guilds[0].roles, name=house),houserole)
                                except:
                                    pass
                            # if otp_info[msg.channel.id][1].lower() in self.groupHeadDict:
                            #     await msg.author.add_roles(get(self.client.guilds[0].roles,id=837027926342893598))
                            old_human=tools.find_duplicate(otp_info[msg.channel.id][1])
                            if old_human:
                                add_on=" Welcome to our community!\n\n"
                                old_USER=await self.client.fetch_user(int(old_human))
                                try:
                                    add_on=f'Welcome back to our community!\n\n'
                                    if int(msg.author.id)!=int(old_human):
                                        await self.client.guilds[0].kick(old_USER)
                                        add_on=f'Welcome back to our community!\n\nWe Kicked your previous account( id: {old_human})'
                                except:
                                    pass
                                tools.change_user_id(otp_info[msg.channel.id][4],otp_info[msg.channel.id][1])
                            else:
                                add_on=" Welcome to our community!\n\n"
                                tools.insert_row(otp_info[msg.channel.id][4],otp_info[msg.channel.id][1])
                            qualrole=get(self.client.guilds[0].roles,id=780935056540827729)
                            try:
                                await msg.author.remove_roles(qualrole)
                            except:
                                pass
                            await msg.author.send(f"""**Success!**
    You are now a Verified member of this server.{add_on}
    **If you like this server, do share our invite link with those who are interested in this degree**
    https://discord.gg/np7EKPcAY3""")
                            otp_info.pop(msg.channel.id)
                            try:
                                await msg.channel.delete()
                                return
                            except:
                                pass
                            
                        else:
                            if otp_info[msg.channel.id][2]==2:
                                await tools.edit_first_message(msg,['otpw',2])
                            if otp_info[msg.channel.id][2]==1:
                                await tools.edit_first_message(msg,['otpw',1])
                            otp_info[msg.channel.id][2]+=1
                    else:
                        await msg.author.send("Verification failed\nReason: Incorrect OTP")  
                        try:
                            await msg.channel.delete()
                        except:
                            print("Failed to delete channel") 
                except:
                    await msg.channel.send("Error from our side")
        except:
            pass

def setup(client):
    client.add_cog(Verification(client))