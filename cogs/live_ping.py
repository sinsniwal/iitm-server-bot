from discord.ext import commands
import discord
import logging
import datetime
from discord.ext import tasks
from config import LIVE_SESSION_PING_ROLE
from typing import List
import re


DATE_FORMAT = "%d-%m-%Y %H:%M"
REMINDER_BEFORE_N_MINUTES = 5


class Event():
    def __init__(self, event: dict) -> None:
        self.name: str = event['summary']
        self.desc: str = event['description']
        self.meet_links: List[str] | None = extractGoogleMeetLinks(
            event['description'])
        self.start: datetime.datetime = datetime.datetime.fromisoformat(
            event['start']['dateTime'])
        self.end: datetime.datetime = datetime.datetime.fromisoformat(
            event['end']['dateTime'])
        self.tz: str = event['start']['timeZone']
        self.id: str = event['id']

    def generateEmbed(self) -> discord.Embed:
        e = discord.Embed(
            title=self.name + " starting now!",
            # description=self.desc,
            color=discord.Colour.brand_green()
        )
        e.add_field(
            name="Time",
            inline=False,
            value=f"<t:{round(self.start.timestamp())}:R>"
        )
        e.add_field(
            name="Meeting Link",
            inline=False,
            value='`No Meeting Link`' if self.meet_links is None else self.meet_links[0]
        )

        e.set_thumbnail(
            url='https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Google_Meet_icon_%282020%29.svg/2491px-Google_Meet_icon_%282020%29.svg.png')
        return e

    def generateReminderEmbed(self) -> discord.Embed:
        e = discord.Embed(
            title=self.name + f" starts in {REMINDER_BEFORE_N_MINUTES} " +
            "minutes" if REMINDER_BEFORE_N_MINUTES > 1 else "minute" + "!",
            # description=self.desc,
            color=discord.Colour.yellow()
        )
        e.add_field(
            name="Time",
            inline=False,
            value=f"<t:{round((self.start - datetime.timedelta(minutes=REMINDER_BEFORE_N_MINUTES)).timestamp())}:R>"
        )
        e.add_field(
            name="Meeting Link",
            inline=False,
            value='`No Meeting Link`' if self.meet_links is None else self.meet_links[0]
        )

        e.set_thumbnail(
            url='https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Google_Meet_icon_%282020%29.svg/2491px-Google_Meet_icon_%282020%29.svg.png')
        return e


class Notification():
    def __init__(self, event: Event, channelId: int, time: datetime.datetime, type: str = "default") -> None:
        self.event = event
        self.channelId = channelId
        self.time = time

    async def send(self, bot):
        channel = bot.get_channel(self.channelId)
        if (type == "reminder"):
            e = self.event.generateReminderEmbed()
        else:
            e = self.event.generateEmbed()
        await channel.send(f'<@&{LIVE_SESSION_PING_ROLE}>', embed=e)


class LivePinger(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger("LivePinger")
        self.logger.info("Loading Live Session Schedule")

        # Initialize Events
        self._events = []
        self._pendingNotifications = []

    def cog_unload(self):
        self.refreshSchedule.cancel()
        self.runNotifications.cancel()

    @tasks.loop(hours=6)
    async def refreshSchedule(self):
        self.logger.info("Updating Schedule List")
        try:

            retrievedData = []  # placeholder for now
            if (len(retrievedData) != 0):
                self.logger.info(
                    "Got "+str(len(retrievedData))+" Live Sessions")
                self._events.clear()
                self._events = [Event({
                    # event['summary'],
                }) for event in retrievedData if isEligible(event)]

                for e in self._events:
                    reminder = e.start - \
                        datetime.timedelta(minutes=REMINDER_BEFORE_N_MINUTES)
                    self._pendingNotifications.append(Notification(
                        e, 1104485755637735456, reminder, "reminder"))  # need to change channel id to be dynamic
                    self._pendingNotifications.append(Notification(
                        e, 1104485755637735456, e.start, "default"))  # need to change channel id to be dynamic

            self.logger.info("Updated Schedule List")
        except Exception as e:
            self.logger.error("Failed to update Schedule List")
            self.logger.error(e)

    @tasks.loop(minutes=1)
    async def runNotifications(self):
        self.logger.info("Checking for notifications to send")
        now = datetime.datetime.now()

        notifications_to_send = [notification for notification in self._pendingNotifications if notification.time.strftime(
            DATE_FORMAT) == now.strftime(DATE_FORMAT)]
        if (not notifications_to_send):
            self.logger.info("No notifications to send")
            return
        self.logger.info(f"Sending {len(notifications_to_send)} notifications")
        new_copy = self._pendingNotifications.copy()
        for n in notifications_to_send:
            await n.send(self.bot)
            new_copy.remove(n)
        self.logger.info("Sent notifications")
        self._pendingNotifications = new_copy
        self.logger.info("Updated pending notifications")

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("Loaded LivePinger")
        self.logger.info("Starting Schedule Refresh Loop")
        self.refreshSchedule.start()
        self.logger.info("Starting Notifications Loop")
        self.runNotifications.start()

    @commands.command()
    async def test_pipeline(self, ctx):
        await ctx.reply("Scheduling notification for 1 minute from now")
        self._pendingNotifications.append(Notification(
            Event({
                "summary": "Test Event",
                "description": "Test Description. https://meet.google.com/not-a-real-meet-link. :)",
                "start": {
                    # add local timezone
                    "dateTime": (datetime.datetime.now() + datetime.timedelta(minutes=1)).isoformat(),
                    "timeZone": "Asia/Kolkata"
                },
                "end": {
                    "dateTime": (datetime.datetime.now() + datetime.timedelta(minutes=2)).isoformat(),
                    "timeZone": "Asia/Kolkata"
                },
                "id": "test"
            }), ctx.channel.id, datetime.datetime.now() + datetime.timedelta(minutes=1)
        ))


async def setup(bot):
    await bot.add_cog(LivePinger(bot))


# Helpers

def isEligible(event: str):
    return True
    if (name is None or name.strip() == ""):
        return False

    name = name.strip().lower()
    checks = []

    # check if stars with live
    checks.append(name.startswith("live"))

    # Add other checks below

    # Check
    return not False in checks


def extractGoogleMeetLinks(text: str):
    if (text is None or text.strip() == ""):
        return None

    return re.findall(r"(https?://meet\.google\.com/[a-zA-Z0-9_-]+)", text)
