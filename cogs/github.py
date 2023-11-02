from __future__ import annotations

import asyncio
import datetime
import os
import re
from typing import TYPE_CHECKING, Any, Callable, Literal, TypeVar

import aiohttp
import discord
import yarl
from discord.ext import commands
from discord.ext.commands.context import Context


if TYPE_CHECKING:
    from _types import Context, GuildContext
    from bot import IITMBot


GUILD_ID = 762774569827565569
CONTRIBUTOR_ROLE_ID = 1114169265822629909

T = TypeVar("T")


class GithubError(commands.CommandError):
    ...


def is_contributor() -> Callable[[T], T]:
    def predicate(ctx: GuildContext) -> bool:
        return ctx.author.get_role(CONTRIBUTOR_ROLE_ID) is not None

    return commands.check(predicate)


def parse_ratelimit_headers(resp: aiohttp.ClientResponse) -> float:
    reset_after = resp.headers.get("X-RateLimit-Reset-After")
    if not reset_after:
        utc = datetime.timezone.utc
        now = datetime.datetime.now(utc)
        reset = datetime.datetime.fromtimestamp(float(resp.headers["X-RateLimit-Reset"]), utc)
        return (reset - now).total_seconds()
    return float(reset_after)


class GitHub(commands.Cog):
    def __init__(self, bot: IITMBot) -> None:
        token = os.environ.get("GITHUB_TOKEN")
        if token is None:
            raise RuntimeError("GITHUB_TOKEN not set. Not loading GitHub cog.")
        self.__token = token
        self.bot = bot
        self.issue = re.compile(r"(?P<repo>backend|frontend|bot)#(?P<number>[0-9]+)")
        self.repos = {
            "backend": "IITM-BS-Codebase/iitm-backend",
            "frontend": "IITM-BS-Codebase/iitm-frontend",
            "bot": "sinsniwal/iitm-server-bot",
        }
        self._req_lock = asyncio.Lock()
        self.__session: aiohttp.ClientSession

    async def cog_load(self) -> None:
        self.__session = aiohttp.ClientSession()

    async def cog_unload(self) -> None:
        await self.__session.close()

    def cog_check(self, ctx: Context) -> bool:
        return ctx.guild is not None and ctx.guild == GUILD_ID

    async def cog_command_error(self, ctx: Context, error: Exception) -> None:
        if isinstance(error, GithubError):
            await ctx.send(f"GitHub Error: {error}")

    async def github_request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        hdrs = {
            "Accept": "application/vnd.github.inertia-preview+json",
            "User-Agent": "IITMBot GitHub Cog",
            "Authorization": f"token {self.__token}",
        }
        req_url = yarl.URL("https://api.github.com") / url
        if headers is not None and isinstance(headers, dict):
            hdrs.update(headers)
        async with self._req_lock:
            async with self.__session.request(method, req_url, params=params, json=data, headers=hdrs) as r:
                remaining = r.headers.get("X-RateLimit-Remaining")
                js = await r.json()
                if r.status == 429 or remaining == "0":
                    # wait before releasing the lock
                    delta = parse_ratelimit_headers(r)
                    await asyncio.sleep(delta)
                    self._req_lock.release()
                    return await self.github_request(method, url, params=params, data=data, headers=headers)
                elif 300 > r.status >= 200:
                    return js
                else:
                    raise GithubError(js["message"])

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if not message.guild or message.guild.id != GUILD_ID:
            return
        if message.author.bot:
            return
        # TODO: should this be gated to certain channels?
        m = self.issue.search(message.content)
        if m is not None:
            url = f'<https://github.com/{self.repos[m.group("repo")]}/issues/{m.group("number")}>'
            await message.channel.send(url)

    async def get_valid_labels(self, repo: Literal["backend", "frontend", "bot"] = "bot") -> set[str]:
        url_path = f"repos/{self.repos[repo]}/labels"
        labels = await self.github_request("GET", url_path)
        return {e["name"] for e in labels}

    async def edit_issue(
        self,
        repo: Literal["backend", "frontend", "bot"],
        number: int,
        *,
        labels: tuple[str, ...] | None = None,
        state: str | None = None,
    ) -> Any:
        url_path = f"repos/{self.repos[repo]}/issues/{number}"
        issue = await self.github_request("GET", url_path)
        if issue.get("pull_request"):
            raise GithubError("That is a pull request, not an issue.")
        current_state = issue.get("state")
        if state == "closed" and current_state == "closed":
            raise GithubError("That issue is already closed.")
        data = {}
        if state:
            data["state"] = state
        if labels:
            current_labels = {e["name"] for e in issue.get("labels", [])}
            valid_labels = await self.get_valid_labels(repo)
            label_set = set(labels)
            diff = [repr(x) for x in (label_set - valid_labels)]
            if diff:
                if len(diff) == 1:
                    human = diff[0]
                elif len(diff) == 2:
                    human = f"{diff[0]} and {diff[1]}"
                else:
                    human = ", ".join(diff[:-1]) + f", and {diff[-1]}"
                raise GithubError(f"Invalid labels passed: {human}")
            data["labels"] = list(current_labels | label_set)
        return await self.github_request("PATCH", url_path, data=data)

    @commands.group(aliases=["gh"])
    async def github(self, ctx: GuildContext) -> None:
        """gitHub administration commands."""
        pass

    @github.command(name="close")
    @is_contributor()
    async def github_close(
        self, ctx: GuildContext, repo: Literal["bot", "backend", "frontend"] | None, number: int, *labels: str
    ) -> None:
        """Closes and optionally labels an issue."""
        repo = repo or "bot"
        js = await self.edit_issue(repo, number, labels=labels, state="closed")
        await ctx.send(f'Successfully closed <{js["html_url"]}>')

    @github.command(name="open")
    @is_contributor()
    async def github_open(
        self, ctx: GuildContext, repo: Literal["bot", "backend", "frontend"] | None, number: int
    ) -> None:
        """Re-opens an issue."""
        repo = repo or "bot"
        js = await self.edit_issue(repo, number, state="open")
        await ctx.send(f'Successfully re-opened <{js["html_url"]}>')

    @github.command(name="label")
    @is_contributor()
    async def github_label(
        self, ctx: GuildContext, repo: Literal["bot", "backend", "frontend"] | None, number: int, *labels: str
    ) -> None:
        """Adds labels to an issue."""
        repo = repo or "bot"
        if not labels:
            await ctx.send("Missing labels to assign.")
            return
        js = await self.edit_issue(repo, number, labels=labels)
        await ctx.send(f'Successfully labeled <{js["html_url"]}>')


async def setup(bot: IITMBot) -> None:
    await bot.add_cog(GitHub(bot))
