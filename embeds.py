import discord
from datetime import datetime


def verification_embed_dm():
    embed = discord.Embed(title="Verification Complete - You're In!",
                          url="https://discord.com/servers/iitm-bs-students-762774569827565569",
                          description="Optimize Your College Server Experience: Get Your Roles and Access Private Channels Tailored to Your Interests! Update Your Level and Get Your Club Roles and Subject Roles in Corresponding Categories. Gain Access to Private Channels and Engage with Like-minded Peers\n\n> Message from ServerBot\n```\nIf you're familiar with discord.py, you can get the server developer role. Check out my GitHub repo link and send a pull request to enhance my functionality.\n```[Github Repo](https://bit.ly/IITMbot)",
                          colour=0x00b0f4,
                          timestamp=datetime.now())
    embed.set_author(name="IITM BS Students",
                     url="https://discord.com/servers/iitm-bs-students-762774569827565569",
                     icon_url="https://cdn.discordapp.com/icons/762774569827565569/a_c1c0b26032fa931e5530abd0fbf0b14f.gif?size=128")

    embed.set_image(
        url="https://i.ibb.co/mFP3KtR/833070-pxplcgyzbd-1490711385.jpg")
    embed.set_footer(text="Have fun ✌️")
    return embed
