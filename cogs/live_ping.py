from __future__ import annotations

import asyncio
import datetime
import logging
import re
from typing import TYPE_CHECKING, Literal, TypedDict
from urllib.parse import quote_plus

import aiohttp
import discord
import Paginator
import yarl
from discord.ext import commands, tasks

from config import LIVE_SESSION_CALENDARS, LIVE_SESSION_PING_ROLE
from utils.formats import plural


if TYPE_CHECKING:
    from typing_extensions import NotRequired

    from bot import IITMBot


DATE_FORMAT = "%d-%m-%Y %H:%M"
REMINDER_BEFORE_N_MINUTES = 5
MEET_LINK_REGEX = re.compile(r"(https?://meet\.google\.com/[a-zA-Z0-9_-]+)")

log = logging.getLogger(__name__)


class EventPayload(TypedDict):
    id: str
    summary: NotRequired[str]
    description: NotRequired[str]
    start: _DateTimePayload
    end: _DateTimePayload


class _DateTimePayload(TypedDict):
    dateTime: str
    timeZone: str


class Event:
    def __init__(self, event: EventPayload) -> None:
        self.name: str = event.get("summary", "No Name")
        self.desc: str = event.get("description", "No Description")
        self.meet_links: list[str] | None = extract_google_meet_links(self.desc)
        self.start: datetime.datetime = datetime.datetime.fromisoformat(event["start"]["dateTime"]).astimezone()
        self.end: datetime.datetime = datetime.datetime.fromisoformat(event["end"]["dateTime"]).astimezone()
        self.tz: str = event["start"]["timeZone"]
        self.id: str = event["id"]

    @property
    def embed(self) -> discord.Embed:
        e = discord.Embed(
            title=f"{self.name} starting now!",
            colour=discord.Colour.brand_green(),
        )
        e.add_field(name="Time", value=discord.utils.format_dt(self.start, "R"))
        if self.meet_links:
            e.add_field(name="Meeting Link", value=self.meet_links[0])

        e.set_thumbnail(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Google_Meet_icon_%282020%29.svg/2491px-Google_Meet_icon_%282020%29.svg.png"
        )
        return e

    @property
    def reminder_embed(self) -> discord.Embed:
        e = discord.Embed(
            title=f"{self.name} starts in {plural(REMINDER_BEFORE_N_MINUTES):minute}!",
            color=discord.Colour.yellow(),
        )
        e.add_field(
            name="Time",
            inline=False,
            value=f"{discord.utils.format_dt(self.start - datetime.timedelta(minutes=REMINDER_BEFORE_N_MINUTES), 'R')}",
        )
        e.add_field(
            name="Meeting Link",
            inline=False,
            value="`No Meeting Link`" if (self.meet_links is None or len(self.meet_links) == 0) else self.meet_links[0],
        )

        e.set_thumbnail(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Google_Meet_icon_%282020%29.svg/2491px-Google_Meet_icon_%282020%29.svg.png"
        )
        return e


class Notification:
    def __init__(
        self,
        event: Event,
        channel_id: int,
        time: datetime.datetime,
        n_type: Literal["default", "reminder", "event"] = "default",
        calendar_name: str = "unknown calendar",
    ) -> None:
        self.event = event
        self.channel_id = channel_id
        self.time = time
        self.type = n_type
        self.calendar_name = calendar_name

    async def send(self, bot: IITMBot):
        channel: discord.TextChannel = bot.get_channel(self.channel_id)  # type: ignore # this is known.
        log.info("chanenel: %s", channel)
        if self.type == "reminder":
            e = self.event.reminder_embed
        else:
            e = self.event.embed
        await channel.send(f"<@&{LIVE_SESSION_PING_ROLE}>", embed=e)


class CalendarOptions:
    def __init__(self, calendar_id: str, start: datetime.datetime, calendar_key: str):
        self.calendar_id = calendar_id
        self.start = start
        self.key = calendar_key

    @property
    def url(self) -> yarl.URL:
        return yarl.URL(
            f"https://clients6.google.com/calendar/v3/calendars/{self.calendar_id}/events?{self.params}", encoded=True
        )

    @property
    def params(self) -> str:
        params = {
            "singleEvents": "true",
            "timeZone": "Asia%2FKolkata",
            "maxAttendees": "1",
            "maxResults": "250",
            "sanitizeHtml": "true",
            "timeMin": quote_plus(self.start.isoformat() + "Z"),
            "timeMax": quote_plus((self.start + datetime.timedelta(weeks=30)).isoformat() + "Z"),
            "key": self.key,
        }
        return "&".join(f"{k}={v}" for k, v in params.items())


class Calendar:
    def __init__(self, options: CalendarOptions, session: aiohttp.ClientSession):
        self.options = options
        self._url = options.url
        self._session = session

    async def get_raw_events(self) -> list[EventPayload] | None:
        async with self._session.get(self._url) as resp:
            log.info("%s %s: %s -> %s", resp.method, resp.url, resp.status, resp.reason)
            if resp.status != 200:
                log.error(await resp.text())
                return None
            data = await resp.json()
            return data.get("items", None)

    def parse_events(self, evs: list[EventPayload]) -> list[Event]:
        return [Event(ev) for ev in evs]


# url = 'https://clients6.google.com/calendar/v3/calendars/c_rviuu7v55mu79mq0im1smptg3o@group.calendar.google.com/events?'
# url += 'calendarId=c_rviuu7v55mu79mq0im1smptg3o%40group.calendar.google.com'
# url += '&singleEvents=true'
# url += '&timeZone=Asia%2FKolkata'
# url += '&maxAttendees=1'
# url += '&maxResults=250'
# url += '&sanitizeHtml=true'
# url += '&timeMin=2023-07-19T00%3A00%3A00%2B05%3A30'
# url += '&timeMax=2023-08-31T00%3A00%3A00%2B05%3A30'
# url += '&key=AIzaSyBNlYH01_9Hc5S1J9vuFmu2nUqBZJNAXxs'


class LivePinger(commands.Cog):
    def __init__(self, bot: IITMBot) -> None:
        self.bot = bot
        log.info("Loading Live Session Schedule")

        # Initialize Events
        self._events: list[Event] = []
        self._pending_notifications: list[Notification] = []
        self._have_data = asyncio.Event()
        self._fetched = asyncio.Event()
        # should be fine, since this is loaded in an async main.
        self._task: asyncio.Task[None] | None = None
        self._current_notification: Notification | None = None
        # notification updates are racy
        self._lock = asyncio.Lock()

    def cog_unload(self):
        if self._task:
            self._task.cancel()
        self.refresh_schedule.cancel()

    @tasks.loop(hours=6)
    async def refresh_schedule(self):
        log.info("Updating Schedule List")
        self._fetched.clear()
        for calendar in LIVE_SESSION_CALENDARS:
            opts = CalendarOptions(
                calendar_id=str(calendar["id"]), start=datetime.datetime.now(), calendar_key=str(calendar["key"])
            )
            cal = Calendar(opts, session=self.bot.session)
            retrieved_data = await cal.get_raw_events()
            if retrieved_data is None:
                log.error("Empty Schedule List")
                return
            if len(retrieved_data) != 0:
                log.info("Got %s Live Sessions", len(retrieved_data))
                self._events.clear()
                self._events = events = cal.parse_events(retrieved_data)
                async with self._lock:
                    for e in events:
                        reminder = e.start - datetime.timedelta(minutes=REMINDER_BEFORE_N_MINUTES)
                        self._pending_notifications.append(
                            Notification(
                                e, int(calendar["channel"]), reminder, "reminder", calendar_name=str(calendar["name"])
                            )
                        )  # need to change channel id to be dynamic
                        self._pending_notifications.append(
                            Notification(e, int(calendar["channel"]), e.start, "default", str(calendar["name"]))
                        )
                        # need to change channel id to be dynamic
                    self._events.sort(key=lambda e: e.start)
                    self._pending_notifications.sort(key=lambda n: n.time)
            log.info("Updated Schedule List")
        self._fetched.set()

    async def get_next_event(self) -> Notification | None:
        log.info("Checking for notifications to send")
        now = discord.utils.utcnow()
        await self._fetched.wait()
        try:
            notification = next(
                notification
                for notification in self._pending_notifications
                if notification.time.astimezone() >= (now + datetime.timedelta(minutes=1))
            )
        except StopIteration:
            log.error("No notifications to send??????")
            return
        log.info("Found notification to send: %s", notification.event.name)
        return notification

    async def wait_for_next_event(self) -> Notification:
        notification = await self.get_next_event()
        if notification is not None:
            self._have_data.set()
            return notification
        self._have_data.clear()
        self._current_notification = None
        await self._have_data.wait()
        notification = await self.get_next_event()
        assert notification is not None
        return notification

    async def call_event(self, notification: Notification) -> None:
        async with self._lock:
            self._pending_notifications.remove(notification)
        await notification.send(self.bot)

    async def dispatch_notifications(self) -> None:
        try:
            while not self.bot.is_closed():
                log.info("Waiting for next event")
                notification = self._current_notification = await self.wait_for_next_event()
                now = discord.utils.utcnow()
                a_minute_ago = now - datetime.timedelta(minutes=1)
                if notification.time >= a_minute_ago:
                    to_sleep = (notification.time - a_minute_ago).total_seconds()
                    await asyncio.sleep(to_sleep)
                await self.call_event(notification)
        except asyncio.CancelledError:
            raise
        except (OSError, discord.ConnectionClosed):
            if self._task:
                self._task.cancel()
            self._task = self.bot.loop.create_task(self.dispatch_notifications())

    async def cog_load(self):
        log.info("Loaded LivePinger")
        self._task = self.bot.loop.create_task(self.dispatch_notifications())
        log.info("Starting Schedule Refresh Loop")
        self.refresh_schedule.start()

    @commands.command()
    async def test_pipeline(self, ctx):
        await ctx.reply("Scheduling notification for 1 minute from now")
        # this doesn't need a lock? i think?
        self._pending_notifications.append(
            Notification(
                Event(
                    {
                        "summary": "Test Event",
                        "description": "Test Description. https://meet.google.com/not-a-real-meet-link. :)",
                        "start": {
                            # add local timezone
                            "dateTime": (datetime.datetime.now() + datetime.timedelta(minutes=1)).isoformat(),
                            "timeZone": "Asia/Kolkata",
                        },
                        "end": {
                            "dateTime": (datetime.datetime.now() + datetime.timedelta(minutes=2)).isoformat(),
                            "timeZone": "Asia/Kolkata",
                        },
                        "id": "test",
                    }
                ),
                ctx.channel.id,
                datetime.datetime.now() + datetime.timedelta(minutes=1),
            )
        )

    @commands.command()
    async def coming_up(self, ctx):
        if ctx.message.author.id != 625907860861091856:
            ctx.reply("you are not allowed to use this command :(")
        if len(self._pending_notifications) == 0:
            await ctx.reply("No upcoming notifications")
            return

        #  partition _pendingNotifications into 5s
        parts = [self._pending_notifications[i : i + 5] for i in range(0, len(self._pending_notifications), 5)]
        embeds = []
        for i in range(len(parts)):
            e = discord.Embed(title=f"Upcoming Notifications", color=discord.Colour.blurple())
            part = parts[i]
            for notification in part:
                e.add_field(
                    name=notification.event.name + " - `" + notification.calendar_name + "`",
                    inline=False,
                    value=f'{discord.utils.format_dt(notification.time, "R")} {"`RMND`" if notification.type == "reminder" else "`EVNT`"}',
                )
            embeds.append(e)
        await Paginator.Simple().start(ctx, embeds)


async def setup(bot: IITMBot):
    await bot.add_cog(LivePinger(bot))


# Helpers


def is_eligible(event: str):
    return True
    if name is None or name.strip() == "":
        return False

    name = name.strip().lower()

    if not name.startswith("live"):
        return False

    # Add other negative checks below.

    return True


def extract_google_meet_links(text: str) -> list[str] | None:
    if not text:
        return None
    return MEET_LINK_REGEX.findall(text)
