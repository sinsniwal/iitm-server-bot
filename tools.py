import sib_api_v3_sdk, discord, http.client, ast,datetime
from sib_api_v3_sdk.rest import ApiException
import configparser
from itertools import cycle
from discord.ext import tasks
import requests
from bs4 import BeautifulSoup


try:
    config = configparser.ConfigParser()
    config.read('../config.ini')
    SIB_API_KEY=config['send_in_blue']['sib_api_key']
except:
    config = configparser.ConfigParser()
    config.read('config.ini')
SIB_API_KEY=config['send_in_blue']['sib_api_key']
REST_API_HOSTNAME=config['ibm_cloud_db2']['rest_api_hostname']
DEPLOYMENT_ID=config['ibm_cloud_db2']['deployment_id']
TOKEN=config['discord_bot']['token']
global otp,otp_info, AUTH_TOKEN
#otp_info[msg.channel.id] = [otp,email,1,level,userid]
otp_info={}
activity= cycle([discord.Activity(type=discord.ActivityType.watching,name='Donnie Darko'),discord.Activity(type=discord.ActivityType.listening,name='Traffic')])


def send_email(name,otp,email_id): 
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = SIB_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    senderSmtp = sib_api_v3_sdk.SendSmtpEmailSender(name="IITM Discord Server",email=config['send_in_blue']['sender_email'])
    htmlcontent=f"""Hi {name},
Please enter the code {otp} on the email verification channel to access the Foundational role.
If you didn't request this code, you can safely ignore this email. Someone else might have typed your email address by mistake.
Don't reply to this mail id if you have any problem,
mail:  mohit.sinsniwal.dev@gmail.com
Thanks! 
IITM B.Sc Students Discord Team"""
    subject="Verification Code for Discord Server"
    sendTo = sib_api_v3_sdk.SendSmtpEmailTo(email=email_id,name=name)
    arrTo = [sendTo] #Adding `to` in a list
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender=senderSmtp,
        to=arrTo,
        html_content=htmlcontent,
        subject=subject) # SendSmtpEmail | Values to send a transactional email
    api_response = api_instance.send_transac_email(send_smtp_email)


def create_embed():
    embed = discord.Embed(
                title='To Proceed further with the verification process, enter your IIT Madras student EmailId [@ds.study.iitm.ac.in]',
                colour=discord.Colour(1038847), 
                description='''We're storing the e-mails in a database to make sure not more than one account verifies by the same  EmailId'''
            )
    embed.set_image(url="https://cdn.discordapp.com/attachments/560753089179680768/594957849797460177/Epic_gif-1.gif") # gif bar
    embed.set_thumbnail(
        url="https://i.ibb.co/VWrY7fv/logotree.jpg"   # thumbnail
    )
    embed.set_author(name="Welcome to our verification process")
    embed.set_footer(
        text=f""
    )
    return embed


def find_duplicate(email):
    global AUTH_TOKEN
    conn = http.client.HTTPSConnection(f"{REST_API_HOSTNAME}")
    payload = "{\"commands\":\"SELECT * FROM VERIFIED where email='"+f"{email[0:-32]}"+"';\",\"limit\":20000,\"separator\":\";\",\"stop_on_error\":\"yes\"}"
    headers = {
        'content-type': "application/json",
        'authorization': f"Bearer {AUTH_TOKEN}",
        'x-deployment-id': f"{DEPLOYMENT_ID}"
        }
    conn.request("POST", "/dbapi/v4/sql_jobs",payload, headers=headers)
    id=ast.literal_eval(conn.getresponse().read().decode("utf-8"))['id']
    conn.request("GET", f"/dbapi/v4/sql_jobs/{id}", headers=headers)
    result=ast.literal_eval(conn.getresponse().read().decode("utf-8"))['results'][0]
    if result['rows_count']:
        return int(result['rows'][0][0])
    return False


def insert_row(user_id,email):
    global AUTH_TOKEN
    conn = http.client.HTTPSConnection(f"{REST_API_HOSTNAME}")
    payload = "{\"commands\":\"INSERT INTO VERIFIED (DISCORD, EMAIL) VALUES ("+f"{int(user_id)}, '{email[0:-32]}'"+");\",\"limit\":20000,\"separator\":\";\",\"stop_on_error\":\"yes\"}"

    headers = {
        'content-type': "application/json",
        'authorization': f"Bearer {AUTH_TOKEN}",
        'x-deployment-id': f"{DEPLOYMENT_ID}"
        }

    conn.request("POST", "/dbapi/v4/sql_jobs",payload, headers=headers)
    res = conn.getresponse()
    data = res.read()
    # print(data.decode('utf-8'))
    id=ast.literal_eval(data.decode("utf-8"))['id']
    conn.request("GET", f"/dbapi/v4/sql_jobs/{id}", headers=headers)
    res = conn.getresponse()
    data = res.read()

def change_user_id(user_id,email):
    # AUTH_TOKEN=auth_token_maker()
    global AUTH_TOKEN
    conn = http.client.HTTPSConnection(f"{REST_API_HOSTNAME}")
    payload = "{\"commands\":\"UPDATE VERIFIED set discord = "+f"{int(user_id)}"+" where email='"+f"{email[0:-32]}"+"';\",\"limit\":20000,\"separator\":\";\",\"stop_on_error\":\"yes\"}"

    headers = {
        'content-type': "application/json",
        'authorization': f"Bearer {AUTH_TOKEN}",
        'x-deployment-id': f"{DEPLOYMENT_ID}"
        }

    conn.request("POST", "/dbapi/v4/sql_jobs",payload, headers=headers)
    res = conn.getresponse()
    data = res.read()
    # print(data.decode('utf-8'))
    id=ast.literal_eval(data.decode("utf-8"))['id']
    conn.request("GET", f"/dbapi/v4/sql_jobs/{id}", headers=headers)
    res = conn.getresponse()
    data = res.read()


def auth_token_maker():
    USERID=config['ibm_cloud_db2']['userid']
    PASSWORD=config['ibm_cloud_db2']['password']
    conn = http.client.HTTPSConnection(f"{REST_API_HOSTNAME}")
    payload=r'{"userid":"%s","password":"%s"}'%(USERID,PASSWORD)
    headers = {
        'content-type': "application/json",
        'x-deployment-id': f"{DEPLOYMENT_ID}",
        'lifetime' : 3600
        }
    conn.request("POST", "/dbapi/v4/auth/tokens", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return ast.literal_eval(data.decode("utf-8"))['token']

@tasks.loop(seconds=1800)
async def change_auth_token():
    global AUTH_TOKEN
    AUTH_TOKEN=auth_token_maker()

@tasks.loop(seconds=130)
async def change_status(client):
    await client.change_presence(activity=next(activity))

@tasks.loop(seconds=100)
async def ticketclose(client):
    #780980984606621696
    open_category=[ele for ele in client.guilds[0].categories if ele.id== 780980984606621696][0]
    for channel in open_category.channels:
        messages = await channel.history(limit=1).flatten()
        if not messages[0].content=="""Error from our side""":
            min30=datetime.datetime(year=2022,month=3,day=4,hour=10,minute=0)-datetime.datetime(year=2022,month=3,day=4,hour=4,minute=0)
            if datetime.datetime.now()-messages[0].created_at>min30: #6hr - 5hr 30 min(indian  timezone)= 30 min
                await messages[0].channel.delete()

# !pip install bs4
def scrape_house_info(soup):
    data=soup.find_all('tr')
    cols=[]
    for col in data[1]:
        cols.append(col.text.lower())
    if len(cols[1:])>3:
        #Type B
        style='B'
        output={}
        for row in data[2:-2]:
            try:
                info=row.find_all('td')
                output[info[0].text.lower()]=[info[2].text.title(),info[3].text.title()]
            except:
                return None
        if not (email_test(output) and house_test_B(output)):
            return None
    else:
        #Type A
        style='A'
        output={}
        for row in data[4:-2]:
            try:
                info=row.find_all('td')
                output[info[0].text.lower()]=info[2].text.title()
            except:
                return None
        if not (email_test(output) and house_test_A(output)):
            return None
    return [style,output]


def house_dict(url):
    soup=BeautifulSoup(requests.get(url).content,"html.parser")
    house=scrape_house_info(soup)
    return house

import re
def email_test(data_dict):
    for email in data_dict:
        if not re.fullmatch('[0-9][0-9][a-z]*[0-9]*@ds.study.iitm.ac.in',email):
            return False
    return True

def house_test_A(data_dict):
    house_set={'Bandipur House', 'Corbett House', 'Gir House', 'Kanha House', 'Kaziranga House', 'Nallamala House', 'Namdapha House', 'Nilgiri House', 'Pichavaram House', 'Saranda House', 'Sundarbans House', 'Wayanad House'}
    try:
        for house in data_dict.values():
            if house not in house_set:
                return False
    except:
        return False
    return True

def house_test_B(data_dict):
    house_set={'Bandipur House', 'Corbett House', 'Gir House', 'Kanha House', 'Kaziranga House', 'Nallamala House', 'Namdapha House', 'Nilgiri House', 'Pichavaram House', 'Saranda House', 'Sundarbans House', 'Wayanad House'}
    for new,old in data_dict.values():
        if new not in house_set:
            return False
        if old not in house_set.union({'No Change'}):
            return False
    return True


def change(output,new=True):
    result={}
    for key,value in output.items():
        if new:
            if value[1]!='No Change':
                result[key]=value
        else:
            if value[1]=='No Change':
                result[key]=value[0]
    return result


def fetch_all():
    # AUTH_TOKEN=auth_token_maker()
    global AUTH_TOKEN
    conn = http.client.HTTPSConnection(f"{REST_API_HOSTNAME}")
    payload = "{\"commands\":\"SELECT * FROM VERIFIED;\",\"limit\":20000,\"separator\":\";\",\"stop_on_error\":\"yes\"}"
    headers = {
        'content-type': "application/json",
        'authorization': f"Bearer {AUTH_TOKEN}",
        'x-deployment-id': f"{DEPLOYMENT_ID}"
        }
    conn.request("POST", "/dbapi/v4/sql_jobs",payload, headers=headers)
    id=ast.literal_eval(conn.getresponse().read().decode("utf-8"))['id']
    conn.request("GET", f"/dbapi/v4/sql_jobs/{id}", headers=headers)
    result=ast.literal_eval(conn.getresponse().read().decode("utf-8"))['results'][0]
    
    return {email.lower()+"@ds.study.iitm.ac.in":discord_id for discord_id,email in result['rows']}



def insert_rows(rows):
    # AUTH_TOKEN=auth_token_maker()
    global AUTH_TOKEN
    conn = http.client.HTTPSConnection(f"{REST_API_HOSTNAME}")
    output=""
    for row in rows:
        output+="('"
        output+=row[:-32]
        output+="',  '"
        output+=rows[row]
        output+="'),"
    output=output[:-1]
    payload = "{\"commands\":\"INSERT INTO house (email, house) VALUES "+output+";\",\"limit\":20000,\"separator\":\";\",\"stop_on_error\":\"yes\"}"
    headers = {
        'content-type': "application/json",
        'authorization': f"Bearer {AUTH_TOKEN}",
        'x-deployment-id': f"{DEPLOYMENT_ID}"
        }

    conn.request("POST", "/dbapi/v4/sql_jobs",payload, headers=headers)
    res = conn.getresponse()
    data = res.read()


def update_rows(rows):
    # AUTH_TOKEN=auth_token_maker()
    global AUTH_TOKEN
    conn = http.client.HTTPSConnection(f"{REST_API_HOSTNAME}")
    output=""
    for email,value in rows:
        output+="UPDATE VERIFIED set house = "+f"{value[0]}"+" where email='"+f"{email[0:-32]}"+"';"
    payload = "{\"commands\":\""+output+"\",\"limit\":3000,\"separator\":\";\",\"stop_on_error\":\"yes\"}"

    headers = {
        'content-type': "application/json",
        'authorization': f"Bearer {AUTH_TOKEN}",
        'x-deployment-id': f"{DEPLOYMENT_ID}"
        }

    conn.request("POST", "/dbapi/v4/sql_jobs",payload, headers=headers)
    res = conn.getresponse()
    data = res.read()



def get_house(email):
    # AUTH_TOKEN=auth_token_maker()
    global AUTH_TOKEN
    conn = http.client.HTTPSConnection(f"{REST_API_HOSTNAME}")
    payload = "{\"commands\":\"SELECT * FROM HOUSE where email='"+f"{email[0:-32]}"+"';\",\"limit\":20000,\"separator\":\";\",\"stop_on_error\":\"yes\"}"
    headers = {
        'content-type': "application/json",
        'authorization': f"Bearer {AUTH_TOKEN}",
        'x-deployment-id': f"{DEPLOYMENT_ID}"
        }
    conn.request("POST", "/dbapi/v4/sql_jobs",payload, headers=headers)
    id=ast.literal_eval(conn.getresponse().read().decode("utf-8"))['id']
    conn.request("GET", f"/dbapi/v4/sql_jobs/{id}", headers=headers)
    result=ast.literal_eval(conn.getresponse().read().decode("utf-8"))['results'][0]
    if result['rows_count']:
        return result['rows'][0][1]
    return False



async  def edit_first_message(msg,mode):
    msgs=await msg.channel.history(oldest_first=True,limit=1).flatten()
    embed=create_embed_mode(mode)
    for  msg in msgs:
        await msg.edit(embed=embed)
        return


#get embed info    
# async  def edit_first_message_get_your_role(client):
#     chnl= client.guilds[0].get_channel(827758351286009886)
#     msgs=await chnl.history(oldest_first=True,limit=1).flatten()
#     for  msg in msgs:
#         print(msg)
#         print(dir(msg))
#         print(msg.embeds[0].to_dict)
#         with open('myembed.txt' ,'w') as f:
#             f.write(str(msg.embeds[0].to_dict()))



def create_embed_mode(mode):
    email='Email    '
    otp_= 'OTP    '
    level='Level    '
    endnote=''
    if mode[0]=='emailr':
        email='Email\t:green_circle:'
        endnote='OTP sent, so check spam and promotions. Please send that OTP here, and you got three attempts.'
    elif  mode[0]=='emailw':
        email='Email\t:red_circle:'
        endnote='Please write your IITM official student Email ID! with @ds.study.iitm.ac.in'
    elif mode[0]=='otpr':
        email='Email\t:green_circle:'
        otp_='OTP\t:green_circle:'
        endnote='Please wait while the bot is working [wait time: less than 10 sec]'
    elif mode[0]=='otpw':
        email='Email    :green_circle:'
        otp_=f'OTP({mode[1]}/3)    :red_circle:'
        endnote='Wrong OTP, please write OTP'
    elif mode[0]=='level':
        if mode[1]=='F':
            level=f'Level    Foundational'
        elif mode[1]=='DP':
            level=f'Level    Direct Diploma P'
        else:
            level=f'Level    Direct Diploma DS'
        email='Email    :green_circle:'
        otp_='OTP    :green_circle:'
        endnote='Please wait while the bot is working [wait time: less than 10 sec]'
    title=f"""{email}

{otp_}

{level}  
"""
    embed = discord.Embed(
                title='',
                colour=discord.Colour(1038847), 
                description=title
            )
    embed.set_image(url="https://cdn.discordapp.com/attachments/560753089179680768/594957849797460177/Epic_gif-1.gif") # gif bar
    embed.set_thumbnail(
        url="https://i.ibb.co/VWrY7fv/logotree.jpg"   # thumbnail
    )
    embed.set_author(name=endnote)
    embed.set_footer(
        text=f""
    )
    return embed
