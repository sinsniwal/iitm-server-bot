import sib_api_v3_sdk, discord, http.client, ast,datetime
from sib_api_v3_sdk.rest import ApiException
import configparser
from itertools import cycle
from discord.ext import tasks

# Attempt to read the configuration file and retrieve the SendinBlue API key.
try:
    config = configparser.ConfigParser()
    config.read('../config.ini')
    SIB_API_KEY=config['send_in_blue']['sib_api_key']
except:
    config = configparser.ConfigParser()
    config.read('config.ini')
SIB_API_KEY=config['send_in_blue']['sib_api_key']

# Attempt to read the configuration file and retrieve the Discord bot token.
TOKEN=config['BOT']['token']
FERNETKEY = config['Key']['fernet'].encode()

# Set the activity status for the Discord bot.
activity= cycle([discord.Activity(type=discord.ActivityType.watching,name='Donnie Darko'),discord.Activity(type=discord.ActivityType.listening,name='Traffic')])


def send_email(name:str,roll_no:str,link:bytes): 
    """
    This function sends an email to the user with the verification link.
    :param name: The name of the user.
    :param roll_no: The roll number of the user.
    :param link: The verification link.
    :return: None
    """
    # Set up the configuration for the SendinBlue API.
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = SIB_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    
	# Set up the email content.
    senderSmtp = sib_api_v3_sdk.SendSmtpEmailSender(name="IITM Discord Server",email=config['send_in_blue']['sender_email'])
    link=link.decode()
    with open('email_template.txt','r') as f:
        htmlcontent=f.read()
    htmlcontent=htmlcontent.replace('{name}',name).replace('{link}',link)
    subject="Verify Your IITM Discord Account Now"
    sendTo = sib_api_v3_sdk.SendSmtpEmailTo(email=roll_no+'@ds.study.iitm.ac.in',name=name)
    arrTo = [sendTo] #Adding `to` in a list
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender=senderSmtp,
        to=arrTo,
        html_content=htmlcontent,
        subject=subject) # SendSmtpEmail | Values to send a transactional email
    
    # Send the email using the SendinBlue API.
    api_response = api_instance.send_transac_email(send_smtp_email)
