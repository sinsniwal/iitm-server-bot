import sib_api_v3_sdk, discord, http.client, ast,datetime
from sib_api_v3_sdk.rest import ApiException
import configparser
from itertools import cycle
from discord.ext import tasks


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
TOKEN=config['BOT']['token']
activity= cycle([discord.Activity(type=discord.ActivityType.watching,name='Donnie Darko'),discord.Activity(type=discord.ActivityType.listening,name='Traffic')])


def send_email(name:str,roll_no:str,link:bytes): 
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = SIB_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    senderSmtp = sib_api_v3_sdk.SendSmtpEmailSender(name="IITM Discord Server",email=config['send_in_blue']['sender_email'])
    link=link.decode()
    htmlcontent="""<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Discord Verification</title>
	<!-- Bootstrap CSS -->
	<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
	<style type="text/css">
		body {
			font-family: 'Arial', sans-serif;
			font-size: 14px;
			line-height: 1.6;
			margin: 0;
			padding: 0;
		}
		.container {
			max-width: 600px;
			margin: 0 auto;
			padding: 20px;
			background-color: rgba(255, 255, 255, 0.9);
			border-radius: 5px;
			box-shadow: 0px 0px 10px #d9d9d9;
		}
		h1 {
			font-size: 36px;
			font-weight: bold;
			margin-bottom: 30px;
			text-align: center;
			color: #424242;
			text-shadow: 2px 2px 3px rgba(0,0,0,0.3);
		}
		p {
			margin-bottom: 20px;
			text-align: justify;
			color: #424242;
			text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
		}
		a {
			color: #ffffff;
			text-decoration: none;
		}
		.button {
			display: inline-block;
			background-color: #7289DA;
			border-radius: 4px;
			color: #ffffff;
			font-size: 18px;
			font-weight: bold;
			margin-top: 20px;
			padding: 10px 20px;
			text-align: center;
			text-decoration: none;
			transition: background-color 0.3s ease;
		}
		.button:hover {
			background-color: #677bc4;
		}
	</style>
</head>
<body>"""+f"""
	<div class="container">
		<h1>Access Private Channels - Verify Your Account on IITM Discord</h1>
		<p>Hello {name},</p>
		<p>Thank you for joining the IITM Discord Server, the ultimate destination for students to connect, collaborate, and exchange ideas with like-minded individuals.</p>
		<p>To gain access to our private channels and unlock the full range of resources available on our server, please click the button below to verify your account:</p>
		<p>If you did not request this verification, you can safely ignore this email. Someone else might have typed your email address by mistake.</p>
		<a href="https://sinsniwal.me/discord-iitm/verify/{link}" class="button">Verify my account</a>
		<p>Thank you for your participation in our community.</p>
		<p>Thanks!<br>Server Bot Developers</p>
	</div>
</body>
</html>
"""
    subject="Verify Your IITM Discord Account Now"
    sendTo = sib_api_v3_sdk.SendSmtpEmailTo(email=roll_no+'@ds.study.iitm.ac.in',name=name)
    arrTo = [sendTo] #Adding `to` in a list
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender=senderSmtp,
        to=arrTo,
        html_content=htmlcontent,
        subject=subject) # SendSmtpEmail | Values to send a transactional email
    api_response = api_instance.send_transac_email(send_smtp_email)
