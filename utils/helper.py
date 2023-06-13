from __future__ import annotations

import os
from datetime import datetime
from itertools import cycle
from typing import TYPE_CHECKING

import discord
import sib_api_v3_sdk
from discord.ext import commands

import config


if TYPE_CHECKING:
    from discord.ext.commands._types import Check

    from _types import Context


# Set the activity status for the Discord bot.
activity = cycle(
    [
        discord.Activity(type=discord.ActivityType.watching, name="Donnie Darko"),
        discord.Activity(type=discord.ActivityType.listening, name="Traffic"),
    ]
)


def admin_only() -> Check[Context]:
    async def pred(ctx: Context) -> bool:
        if ctx.author.id != config.ADMIN_ID:
            raise commands.CheckFailure()
        return True

    return commands.check(pred)


def verification_embed_dm() -> discord.Embed:
    embed = discord.Embed(
        title="Verification Complete - You're In!",
        url="https://discord.com/servers/iitm-bs-students-762774569827565569",
        description="Optimize Your College Server Experience: Get Your Roles and Access Private Channels Tailored to Your Interests! Update Your Level and Get Your Club Roles and Subject Roles in Corresponding Categories. Gain Access to Private Channels and Engage with Like-minded Peers\n\n> Message from ServerBot\n```\nIf you're familiar with discord.py, you can get the server developer role. Check out my GitHub repo link and send a pull request to enhance my functionality.\n```[Github Repo](https://bit.ly/IITMbot)",
        colour=0x00B0F4,
        timestamp=datetime.now(),
    )
    embed.set_author(
        name="IITM BS Students",
        url="https://discord.com/servers/iitm-bs-students-762774569827565569",
        icon_url="https://cdn.discordapp.com/icons/762774569827565569/a_c1c0b26032fa931e5530abd0fbf0b14f.gif?size=128",
    )

    embed.set_image(url="https://i.ibb.co/mFP3KtR/833070-pxplcgyzbd-1490711385.jpg")
    embed.set_footer(text="Have fun ✌️")
    return embed


def send_email(name: str, roll_no: str, link: bytes) -> None:
    """
    This function sends an email to the user with the verification link.
    :param name: The name of the user.
    :param roll_no: The roll number of the user.
    :param link: The verification link.
    :return: None
    """
    # Set up the configuration for the SendinBlue API.
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = os.environ.get("SIB_API_KEY")
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Set up the email content.
    senderSmtp = sib_api_v3_sdk.SendSmtpEmailSender(
        name="IITM Discord Server", email=os.environ.get("SIB_SENDER_EMAIL")
    )
    print(link.decode())
    with open("utils/email_template.txt", "r") as f:
        htmlcontent = f.read()
    htmlcontent = htmlcontent.replace("{name}", name).replace("{link}", link.decode())
    subject = "Verify Your IITM Discord Account Now"
    sendTo = sib_api_v3_sdk.SendSmtpEmailTo(email=roll_no + "@ds.study.iitm.ac.in", name=name)
    arrTo = [sendTo]  # Adding `to` in a list
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender=senderSmtp, to=arrTo, html_content=htmlcontent, subject=subject
    )  # SendSmtpEmail | Values to send a transactional email

    # Send the email using the SendinBlue API.
    api_instance.send_transac_email(send_smtp_email)
