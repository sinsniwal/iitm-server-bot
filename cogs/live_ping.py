from discord.ext import commands
import discord
import logging
import datetime
import urllib
import re
import requests
import schedule
import threading
import time
from config import LIVE_SESSION_PING_ROLE

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


class CalendarInterface():
    def __init__(self, cId: str = None, ) -> None:
        self.url = "https://clients6.google.com/calendar/v3/calendars/"
        self.url += cId
        self.url += "/events?"
        self.url += "calendarId="
        self.url += cId
        self.url += "&singleEvents=true"
        self.url += "&timeZone=Asia%2FKolkata"
        self.url += "&maxAttendees=1"
        self.url += "&maxResults=250"
        self.url += "&sanitizeHtml=true"
        self.url += "&key=AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs"

    def getEvents(self, start: datetime.datetime = None):
        qUrl = self.url.copy()
        qUrl += "&timeMin="
        qUrl += urllib.parse.quote(start.isoformat(), safe='')
        qUrl += "&timeMax="
        qUrl += urllib.parse.quote((start +
                                    datetime.timedelta(days=30)).isoformat(), safe='')
        return requests.get(qUrl).json()['items']


class LivePinger(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger("LivePinger")
        self.logger.info("Loading Live Session Schedule")
        self.CI = CalendarInterface(
            cId='c_rviuu7v55mu79mq0im1smptg3o%40group.calendar.google.com'
        )
        self.scheduleList = []

        async def sendNotificationWithDateCheck(channelId, event: dict):
            now = datetime.datetime.now(tz=event['start'].tzinfo)
            if (now > event['start']):
                return schedule.CancelJob
            if (now.date() == event['start'].date()):
                # main shit
                channel = self.bot.get_channel(channelId)
                e = discord.Embed(
                    title=event['name'] + ' starts ' +
                    f'<t:{round(event["start"].timestamp())}:R>',
                    timestamp=now,
                    color=discord.Colour.brand_green(),
                    url=event['meet_links'][0],
                )
                e.add_field(
                    name="Meeting Link",
                    inline=False,
                    value=event['meet_links'][0]
                )
                e.set_thumbnail(
                    url='https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Google_Meet_icon_%282020%29.svg/2491px-Google_Meet_icon_%282020%29.svg.png')
                await channel.send(f'<@&{LIVE_SESSION_PING_ROLE}>', embed=e)
                return schedule.CancelJob

        def scheduleNotifications(channelId: int = None, events: list = None):
            if (None in [channelId, events]):
                return
            for event in events:
                schedule.every().day.at(
                    event['start'].strftime("%H:%M:%S")).do(sendNotificationWithDateCheck, channelId=channelId, event=event)

        def updateScheduleList():
            self.logger.info("Updating Live Sessions")
            events = self.CI.getEvents(start=datetime.datetime.now())
            if (len(events) > 0):
                self.logger.info("Got "+str(len(events))+" Live Sessions")
                self.scheduleList.clear()
                schedule.clear()
            for event in events:
                if event['status'] == 'confirmed' and isEligible(event['summary']):
                    d = {
                        'name': event['summary'],
                        'desc': event['description'],
                        'meet_links':  extractGoogleMeetLink(event['description']),
                        'start': datetime.datetime.strptime(event['start']['dateTime'], "%Y-%m-%dT%H:%M:%S%z"),
                        'end': datetime.datetime.strptime(event['end']['dateTime'], "%Y-%m-%dT%H:%M:%S%z"),
                        'tz': event['start']['timeZone'],
                        'id': event['id']
                    }
                    self.scheduleList.append(d)
            self.logger.info("Updated Live Sessions")
            scheduleNotifications(
                channelId=882288447282696704, events=self.scheduleList)
        schedule.every(6).hours.do(updateScheduleList)
        self.sendNotificationWithDateCheck = sendNotificationWithDateCheck
        self.scheduleNotifications = scheduleNotifications

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info("Loaded LivePinger")
        self.logger.info("Scheduling Refresh Task")

        def run_scheduled_jobs():
            while True:
                schedule.run_pending()
                time.sleep(1)

        self.scheduleNotifications()

        schedule_thread = threading.Thread(target=run_scheduled_jobs)
        schedule_thread.start()

    @commands.command()
    async def testalert(self, ctx):
        e = {
            'name': 'Test Event',
            'desc': 'Test Description',
            'meet_links': ['https://meet.google.com/not-a-real-link'],
            'start': datetime.datetime.now() + datetime.timedelta(hours=1),
            'end': datetime.datetime.now() + datetime.timedelta(hours=2),
            'tz': 'Asia/Kolkata',
            'id': 'test'
        }
        await self.sendNotificationWithDateCheck(ctx.channel.id, e)


async def setup(bot):
    await bot.add_cog(LivePinger(bot))


# Helpers

def isEligible(name: str = None):

    if (name is None or name.strip() == ""):
        return False

    name = name.strip().lower()
    checks = []

    # check if stars with live
    checks.append(name.startswith("live"))

    # Add other checks below

    # Check
    return not False in checks


def extractGoogleMeetLink(text: str = None):
    if (text is None or text.strip() == ""):
        return None

    return re.findall(r"(https?://meet\.google\.com/[a-zA-Z0-9_-]+)", text)
