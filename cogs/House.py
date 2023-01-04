import  discord,tools
from discord.ext import commands
from discord.utils import get


class House(commands.Cog):

    def  __init__(self,client):
        self.client=client
#        print(len(client.guilds))
#        self.houserole=get(client.guilds[0].roles, id=835238631848804353)
        
    @commands.command()
    async def house(self, ctx, *,url):
        if ctx.channel.id==766072627311673377:
            print(url)
            data=tools.house_dict(url)
            print(data)
            if data:
                if data[0]=='A':
                    try:
                        await ctx.send('typeA')
                        info=data[1]
                        try:
                            tools.insert_rows(info)
                        except:
                            pass
                        discord_users=tools.fetch_all()
                        for email in info:
                            if email in discord_users:
                                try:
                                    member= await self.client.guilds[0].fetch_member(int(discord_users[email]))
                                    self.houserole=get(ctx.guild.roles, id=835238631848804353)
                                    if self.houserole not in member.roles:
                                        await member.add_roles(get(self.client.guilds[0].roles, name=info[email]))
                                        await member.add_roles(self.houserole)
                                        print(email,member.name,'given role',info[email])
                                    else:
                                        print('else')
                                except:
                                    print(email, 'error',member.name)
                    except:
                        pass
                else:
                    try:
                        print('1')
                        info=data[1]
                        print('2')
                        result=tools.change(info,False)  #email:house
                        print('3')
                        try:
                            tools.insert_rows(result)
                        except:
                            print('insert_rows issue')
                        print('4')
                        discord_users=tools.fetch_all()
                        print("5")
                        for email in result:
                            print("6")
                            if email in discord_users:
                                print("7")
                                try:
                                    print("8")
                                    member= await self.client.guilds[0].fetch_member(discord_users[email.lower()])
                                    print('9')
                                    if self.houserole not in member.roles:
                                        print("10")
                                        await member.add_roles(get(self.client.guilds[0].roles, name=result[email.lower()]))
                                        print("11")
                                        await member.add_roles(self.houserole)
                                        print("12")
                                        print(email,member.name,'given role',info[email])
                                        print("13")
                                except:
                                    print(email, 'error',member.name)
                        print('16')
                        result=tools.change(info,True) #email:[new,old]
                        print("17")
                        try:
                            tools.update_rows(result)
                        except:
                            print("update_rows issue")
                        discord_users=tools.fetch_all()
                        for email in result:
                            if email in discord_users:
                                try:
                                    newrole= get(self.client.guilds[0].roles, name=result[email][0])
                                    print('1')
                                    member= await self.client.guilds[0].fetch_member(discord_users[email])

                                    print("2")
                                    if self.houserole not in member.roles:
                                        print('3')
                                        await member.add_roles(get(self.client.guilds[0].roles, name=result[email][0]))
                                        await member.add_roles(self.houserole)
                                        print(email,member.name,'given role',info[email][0])
                                    elif newrole not in member.roles:
                                        print("4")
                                        await member.remove_roles(get(self.client.guilds[0].roles, name=result[email][1]))
                                        await member.add_roles(get(self.client.guilds[0].roles, name=result[email][0]))

                                except:
                                    print(email, 'error',member.name)
                    except:
                        print("error")

            else:
                await ctx.send('Please check url and content')
        pass
    
def  setup(client):
    client.add_cog(House(client))
