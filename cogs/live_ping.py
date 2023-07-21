import re
import requests
import logging
import datetime

import discord
from discord.ext import commands
from discord.ext import tasks
from typing import List

from config import LIVE_SESSION_PING_ROLE, LIVE_SESSION_CALENDARS


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
        self.type = type

    async def send(self, bot):
        channel = bot.get_channel(self.channelId)
        if (type == "reminder"):
            e = self.event.generateReminderEmbed()
        else:
            e = self.event.generateEmbed()
        await channel.send(f'<@&{LIVE_SESSION_PING_ROLE}>', embed=e)


class CalendarOptions():
    def __init__(self, calendar_id: str, start: datetime.datetime, calendarKey: str):
        self.calendar_id = calendar_id
        self.start = start
        self.key = calendarKey

    def getUrlForDayEvents(self) -> str:
        url = "https://clients6.google.com/calendar/v3/calendars/"+self.calendar_id+"/events?"
        url += "calendarId="+self.calendar_id
        url += "&singleEvents=true"
        url += "&timeZone=Asia%2FKolkata"
        url += "&maxAttendees=1"
        url += "&maxResults=250"
        url += "&sanitizeHtml=true"
        url += "&timeMin=" + \
            convertToUrlSafe(addISTtoISO(self.start.isoformat()))  # start
        url += "&timeMax=" + \
            convertToUrlSafe(
                addISTtoISO((self.start + datetime.timedelta(weeks=30)).isoformat()))  # end
        url += "&key="+self.key
        return url


class Calendar():
    def __init__(self, options: CalendarOptions):
        self.options = options
        self._url = options.getUrlForDayEvents()

    def getRawEvents(self) -> list | None:
        try:
            rawEvents = requests.get(self._url).json()['items']
            return rawEvents
        except:
            return None

    def getEvents(self) -> List[Event] | None:
        try:
            rawEvents = self.getRawEvents()
            if (rawEvents is None):
                return None
            events = [Event(rawEvent) for rawEvent in rawEvents]
            return events
        except:
            return None

# url = "https://clients6.google.com/calendar/v3/calendars/c_rviuu7v55mu79mq0im1smptg3o@group.calendar.google.com/events?"
# url += "calendarId=c_rviuu7v55mu79mq0im1smptg3o%40group.calendar.google.com"
# url += "&singleEvents=true"
# url += "&timeZone=Asia%2FKolkata"
# url += "&maxAttendees=1"
# url += "&maxResults=250"
# url += "&sanitizeHtml=true"
# url += "&timeMin=2023-07-19T00%3A00%3A00%2B05%3A30"
# url += "&timeMax=2023-08-31T00%3A00%3A00%2B05%3A30"
# url += "&key=AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs"


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
            for calendar in LIVE_SESSION_CALENDARS:
                opts = CalendarOptions(
                    calendar_id=str(calendar['id']),
                    start=datetime.datetime.now(),
                    calendarKey=str(calendar['key'])
                )
                cal = Calendar(opts)
                retrievedData = cal.getRawEvents()
                if retrievedData is None:
                    self.logger.error("Empty Schedule List")
                    return
                if (len(retrievedData) != 0):
                    self.logger.info(
                        "Got "+str(len(retrievedData))+" Live Sessions")
                    self._events.clear()
                    self._events = (events := [Event(event)
                                    for event in retrievedData if isEligible(event)])

                    for e in events:
                        reminder = e.start - datetime.timedelta(
                            minutes=REMINDER_BEFORE_N_MINUTES)
                        self._pendingNotifications.append(Notification(
                            e, int(calendar['channel']), reminder, "reminder"))  # need to change channel id to be dynamic
                        self._pendingNotifications.append(Notification(
                            e, int(calendar['channel']), e.start, "default"))
                        # need to change channel id to be dynamic
                    self._events.sort(key=lambda e: e.start)
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

    @commands.command()
    async def coming_up(self, ctx):
        if(ctx.message.author.id != 625907860861091856) ctx.reply('you are not allowed to use this command :(')
        if (len(self._pendingNotifications) == 0): 
            await ctx.reply("No upcoming notifications")
            return
        e = discord.Embed(
             title="Upcoming Live Sessions",
             color=discord.Colour.blurple()
        )
        for notification in self._pendingNotifications[0:5]:
            e.add_field(
                 name=notification.event.name +
                 ("`RMND`" if notification.type == "reminder" else "`EVNT`"),
                 inline=False,
                 value=f"<t:{round(notification.time.timestamp())}:R>"
            )
        await ctx.reply(embed=e)


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


def convertToUrlSafe(url: str):
    conversionTable = {
        "/": "%2F",
        ":": "%3A",
        "+": "%2B",
        "-": "%2D"
    }
    for character, replacement in conversionTable.items():
        url = url.replace(character, replacement)

    return url


def addISTtoISO(iso: str):
    if (not iso.endswith('+05:30')):
        iso += '+05:30'
    return iso
