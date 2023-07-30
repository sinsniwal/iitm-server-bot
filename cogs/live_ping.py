from __future__ import annotations

import asyncio
import datetime
import logging
import re
from typing import TYPE_CHECKING, Literal, TypedDict
from urllib.parse import quote_plus

import aiohttp
import discord
import yarl
from discord.ext import commands, menus, tasks

from config import LIVE_SESSION_CALENDARS, LIVE_SESSION_PING_ROLE
from utils.formats import plural
from utils.helper import admin_only
from utils.paginator import BotPages, ListPageSource


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
    conferenceData: _ConferenceData


class _DateTimePayload(TypedDict):
    dateTime: str
    timeZone: str


class _ConferenceData(TypedDict):
    conferenceId: str
    conferenceSolution: _ConferenceSolution


class _ConferenceSolution(TypedDict):
    key: _ConferenceSolutionKey


class _ConferenceSolutionKey(TypedDict):
    type: Literal["eventHangout", "eventNamedHangout", "hangoutsMeet", "addOn"]


class _EventSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=5)

    def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        embed = discord.Embed(title=f"Upcoming Notifications", color=discord.Colour.blurple())
        for _, notification in enumerate(entries, start=offset):
            embed.add_field(
                name=notification.event.name + " - `" + notification.calendar_name + "`",
                inline=False,
                value=f'{discord.utils.format_dt(notification.time, "R")} {"`RMND`" if notification.type == "reminder" else "`EVNT`"}',
            )
        return embed


class Event:
    def __init__(self, event: EventPayload) -> None:
        self.name: str = event.get("summary", "No Name")
        self.desc: str = event.get("description", "No Description")
        self.start: datetime.datetime = datetime.datetime.fromisoformat(event["start"]["dateTime"]).astimezone()
        self.end: datetime.datetime = datetime.datetime.fromisoformat(event["end"]["dateTime"]).astimezone()
        self.tz: str = event["start"]["timeZone"]
        self.id: str = event["id"]
        cData = event.get("conferenceData", None)
        if not cData:
            match = MEET_LINK_REGEX.search(self.desc)
            if match is not None:
                self.meet_link = match.group()
            else:
                self.meet_link = None
        else:
            event_type = event["conferenceData"]["conferenceSolution"]["key"]["type"]
            if event_type == "hangoutsMeet":
                self.meet_link = f'https://meet.google.com/{event["conferenceData"]["conferenceId"]}'
            else:
                self.meet_link = None

    @property
    def embed(self) -> discord.Embed:
        e = discord.Embed(
            title=f"`{self.name}` starting now!",
            colour=discord.Colour.brand_green(),
        )
        e.add_field(name="Time", value=discord.utils.format_dt(self.start, "R"))
        if self.meet_link:
            e.add_field(name="Meeting Link", value=self.meet_link, inline=False)

        # e.set_thumbnail(
        #     url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Google_Meet_icon_%282020%29.svg/2491px-Google_Meet_icon_%282020%29.svg.png"
        # )
        return e

    @property
    def reminder_embed(self) -> discord.Embed:
        e = discord.Embed(
            title=f"`{self.name}` starts in {plural(REMINDER_BEFORE_N_MINUTES):minute}!",
            color=discord.Colour.yellow(),
        )
        e.add_field(
            name="Time",
            inline=False,
            value=f"{discord.utils.format_dt(self.start, 'R')}",
        )
        if self.meet_link:
            e.add_field(name="Meeting Link", value=self.meet_link, inline=False)
        # e.set_thumbnail(
        #     url="https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Google_Meet_icon_%282020%29.svg/2491px-Google_Meet_icon_%282020%29.svg.png"
        # )
        return e


class Notification:
    def __init__(
        self,
        event: Event,
        channel_id: int,
        time: datetime.datetime,
        n_type: Literal["default", "reminder", "event"] = "default",
        calendar_name: str = "unknown calendar",
        icon_url: str = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Google_Meet_icon_%282020%29.svg/2491px-Google_Meet_icon_%282020%29.svg.png",
    ) -> None:
        self.event = event
        self.channel_id = channel_id
        self.time = time.astimezone()
        self.type = n_type
        self.calendar_name = calendar_name
        self.icon_url = icon_url

    async def send(self, bot: IITMBot):
        channel: discord.TextChannel = bot.get_channel(self.channel_id)  # type: ignore
        log.info(f"channel: name -> {str(channel.name)}  | id -> {str(channel.id)}")
        if self.type == "reminder":
            e = self.event.reminder_embed
        else:
            e = self.event.embed
        e.set_thumbnail(
            url=self.icon_url,
        )
        e.set_footer(text=f"🗓️ {self.calendar_name}")
        await channel.send(f"<@&{LIVE_SESSION_PING_ROLE}>", embed=e)


class CalendarOptions:
    def __init__(
        self,
        calendar_id: str,
        start: datetime.datetime,
        calendar_key: str,
        icon: str = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Google_Meet_icon_%282020%29.svg/2491px-Google_Meet_icon_%282020%29.svg.png",
    ):
        self.calendar_id = calendar_id
        self.start = start
        self.key = calendar_key
        self.icon = icon

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
            "timeMax": quote_plus((self.start + datetime.timedelta(days=3)).isoformat() + "Z"),
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
        l = []
        for ev in evs:
            try:
                l.append(Event(ev))
            except Exception as e:
                log.error("Error parsing event -> " + str(e))
                log.error(str(ev))
        return l


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
                calendar_id=str(calendar["id"]),
                start=datetime.datetime.now(),
                calendar_key=str(calendar["key"]),
                icon=str(calendar["icon"]),
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
                                event=e,
                                channel_id=int(calendar["channel"]),
                                time=reminder,
                                n_type="reminder",
                                calendar_name=str(calendar["name"]),
                                icon_url=str(calendar["icon"]),
                            )
                        )
                        # need to change channel id to be dynamic
                        self._pending_notifications.append(
                            Notification(
                                event=e,
                                channel_id=int(calendar["channel"]),
                                time=e.start,
                                n_type="default",
                                calendar_name=str(calendar["name"]),
                                icon_url=str(calendar["icon"]),
                            )
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
                if notification.time >= now and notification is not self._current_notification
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
        log.info('sending notification "%s"', notification.event.name)
        async with self._lock:
            self._pending_notifications.remove(notification)
        await notification.send(self.bot)

    async def dispatch_notifications(self) -> None:
        try:
            while not self.bot.is_closed():
                log.info("Waiting for next event")
                notification = self._current_notification = await self.wait_for_next_event()
                now = discord.utils.utcnow()
                if notification.time > now:
                    log.info('sleeping until "%s"', notification.time)
                    to_sleep = (notification.time - now).total_seconds()
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
    @admin_only()
    async def test_live_session(self, ctx, include_conference: str = "yes"):
        if (include_conference := include_conference.lower().strip()) not in ["yes", "no"]:
            await ctx.reply("Invalid argument. Please use `yes` or `no`")
            return

        await ctx.reply(
            f"Test Notification for 1 Minute from now\n`includeConferenceDetails` -> `{include_conference.upper()}`"
        )
        # this doesn't need a lock? i think?
        self._pending_notifications.insert(
            0,
            Notification(
                event=Event(get_test_event_data(include_conference=(include_conference == "yes"))),
                channel_id=ctx.channel.id,
                time=datetime.datetime.now() + datetime.timedelta(minutes=1),
                calendar_name="Pinger Test Calendar",
                n_type="default",
                icon_url="https://i.imgur.com/HJo8u3y.png",
            ),
        )
        # restart the task
        if self._task:
            self._task.cancel()
        self._task = self.bot.loop.create_task(self.dispatch_notifications())

    @commands.command()
    @admin_only()
    async def coming_up(self, ctx):
        if len(self._pending_notifications) == 0:
            await ctx.reply("No upcoming notifications")
            return

        source = NotificationPageSource(self._pending_notifications, per_page=5)
        pages = BotPages(source, ctx=ctx)
        await pages.start()


class NotificationPageSource(ListPageSource[Notification]):
    async def format_page(self, menu: BotPages, entries: list[Notification]) -> discord.Embed:
        e = discord.Embed(colour=discord.Colour.blurple())
        for notification in entries:
            e.add_field(
                name=f"{notification.event.name} - `{notification.calendar_name}`",
                value=f'{discord.utils.format_dt(notification.time, "R")} {"`RMND`" if notification.type == "reminder" else "`EVNT`"}',
                inline=False,
            )
        return e


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


def get_test_event_data(include_conference: bool = True) -> EventPayload:
    if include_conference:
        return {
            "summary": "Test Event",
            "description": "Test Description. https://meet.google.com/des-scrip-tion. :)",
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
            "conferenceData": {
                "conferenceId": "con-fer-ence",
                "conferenceSolution": {
                    "key": {
                        "type": "hangoutsMeet",
                    }
                },
            },
        }
    else:
        # don't change this
        return {
            "summary": "Test Event",
            "description": "Test Description. https://meet.google.com/des-scrip-tion. :)",
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
        }  # type: ignore
