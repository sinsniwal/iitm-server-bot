from __future__ import annotations

import io
import logging
import math
import textwrap
import traceback
from contextlib import redirect_stdout
from typing import TYPE_CHECKING, Any, Awaitable, Callable

import discord
from discord.ext import commands
from discord.ext.commands.errors import ExtensionNotFound

import config


if TYPE_CHECKING:
    from _types import Context
    from bot import IITMBot


class Dev(commands.Cog):
    def __init__(self, bot: IITMBot):
        self.logger = logging.getLogger("Dev")
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.logger.info("Loaded Dev")

    def cleanup_code(self, content: str) -> str:
        """
        Remove code-block from eval
        """
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])

        return content.strip("`\n")

    def get_syntax_error(self, e: SyntaxError) -> str:
        if e.text is None:
            return f"```py\n{e.__class__.__name__}: {e}\n```"
        return f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```'

    @commands.is_owner()
    @commands.command(name="eval")
    async def eval(self, ctx: Context, *, body: str) -> None:
        """Evaluates a code"""
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "self": self,
            "math": math,
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            await ctx.send(f"```py\n{e.__class__.__name__}: {e}\n```")
            return

        func: Callable[..., Awaitable[Any]] = env["func"]  # type: ignore
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f"```py\n{value}{traceback.format_exc()}\n```")
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction("\N{THUMBS UP SIGN}")
            except Exception as _:
                await ctx.message.add_reaction("\N{THUMBS DOWN SIGN}")
                pass

            if ret is None:
                self.logger.info(f"Output chars: {len(str(value))}")
                if value:
                    if len(str(value)) >= 2000:
                        await ctx.send(
                            f"Returned over 2k chars, sending as file instead.\n"
                            f"(first 1.5k chars for quick reference)\n"
                            f"```py\n{value[0:1500]}\n```",
                            file=discord.File(io.BytesIO(value.encode()), filename="output.txt"),
                        )
                    else:
                        await ctx.send(f"```py\n{value}\n```")
            else:
                self.logger.info(f"Output chars: {len(str(value)) + len(str(ret))}")
                self._last_result = ret
                if len(str(value)) + len(str(ret)) >= 2000:
                    await ctx.send(
                        f"Returned over 2k chars, sending as file instead.\n"
                        f"(first 1.5k chars for quick reference)\n"
                        f'```py\n{f"{value}{ret}"[0:1500]}\n```',
                        file=discord.File(io.BytesIO(f"{value}{ret}".encode()), filename="output.txt"),
                    )
                else:
                    await ctx.send(f"```py\n{value}{ret}\n```")

    @commands.is_owner()
    @commands.command(name="reload", hidden=True)
    async def reload(self, ctx: Context, *, module_name: str) -> None:
        """Reload a module"""
        try:
            try:
                await self.bot.unload_extension(module_name)
            except commands.errors.ExtensionNotLoaded:
                await ctx.send(f"Module not loaded. Trying to load it.", delete_after=6)

            await self.bot.load_extension(module_name)
            await ctx.send("Module Loaded")

        except ExtensionNotFound:
            await ctx.send(
                f"Module not found. Possibly, wrong module name provided.",
                delete_after=10,
            )
        except Exception as e:
            self.logger.error("Unable to load module.")
            self.logger.error("{}: {}".format(type(e).__name__, e))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def kill(self, ctx: Context) -> None:
        """Kill the bot"""
        await ctx.send("Bravo 6, going dark o7")
        await self.bot.close()

    @commands.command()
    @commands.is_owner()
    async def sync_apps(self, ctx: Context) -> None:
        await ctx.bot.tree.sync(guild=discord.Object(config.PRIMARY_GUILD_ID))
        await ctx.reply("Synced local guild commands")

    @commands.command()
    @commands.is_owner()
    async def clear_apps(self, ctx: Context) -> None:
        ctx.bot.tree.clear_commands(guild=discord.Object(config.PRIMARY_GUILD_ID))
        ctx.bot.tree.clear_commands(guild=None)
        await ctx.bot.tree.sync(guild=discord.Object(config.PRIMARY_GUILD_ID))
        await ctx.bot.tree.sync()

        await ctx.send("cleared all commands")


async def setup(bot: IITMBot):
    await bot.add_cog(Dev(bot))
