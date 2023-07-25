"""
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Literal, Optional, TypeVar, overload

import discord
from discord.ext import commands


if TYPE_CHECKING:
    from _types import Context


T = TypeVar("T")


class NumberedPageModal(discord.ui.Modal, title="Go to page"):
    page = discord.ui.TextInput(label="Page", placeholder="Enter a number", min_length=1)

    def __init__(self, max_pages: Optional[int]) -> None:
        super().__init__()
        if max_pages is not None:
            as_string = str(max_pages)
            self.page.placeholder = f"Enter a number between 1 and {as_string}"
            self.page.max_length = len(as_string)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        self.interaction = interaction
        self.stop()


class PageSource(Generic[T]):
    async def _prepare_once(self) -> None:
        try:
            # I don't feel like formatting hasattr with
            # the proper mangling
            # read this as follows:
            # if hasattr(self, '__prepare')
            # except that it works as you expect
            self.__prepare
        except AttributeError:
            await self.prepare()
            self.__prepare = True

    async def prepare(self) -> None:
        return

    def is_paginating(self) -> bool:
        raise NotImplementedError

    def get_max_pages(self) -> Optional[int]:
        return None

    async def get_page(self, page_number: int) -> T:
        raise NotImplementedError

    async def format_page(self, menu: BotPages, page: T) -> str | discord.Embed | dict[str, Any]:
        raise NotImplementedError


class BotPages(discord.ui.View, Generic[T]):
    def __init__(self, source: PageSource[T], *, ctx: Context, check_embeds: bool = True, compact: bool = False):
        super().__init__()
        self.source = source
        self.check_embeds = check_embeds
        self.ctx = ctx
        self.message: Optional[discord.Message] = None
        self.current_page = 0
        self.compact = compact
        self.clear_items()
        self.fill_items()

    def fill_items(self) -> None:
        if not self.compact:
            self.numbered_page.row = 1
            self.stop_pages.row = 1
        if self.source.is_paginating():
            max_pages = self.source.get_max_pages()
            use_last_and_first = max_pages is not None and max_pages >= 2
            if use_last_and_first:
                self.add_item(self.go_to_first_page)
            self.add_item(self.go_to_previous_page)
            if not self.compact:
                self.add_item(self.go_to_current_page)
            self.add_item(self.go_to_next_page)
            if use_last_and_first:
                self.add_item(self.go_to_last_page)
            if not self.compact:
                self.add_item(self.numbered_page)
            self.add_item(self.stop_pages)

    async def _get_kwargs_from_page(self, page: T) -> dict[str, Any]:
        value = await discord.utils.maybe_coroutine(self.source.format_page, self, page)
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            return {"content": value, "embed": None}
        elif isinstance(value, discord.Embed):
            return {"embed": value, "content": None}
        else:
            return {}

    async def show_page(self, interaction: discord.Interaction, page_number: int) -> None:
        page = await self.source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(page_number)
        if kwargs:
            if interaction.response.is_done():
                if self.message:
                    await self.message.edit(**kwargs, view=self)
            else:
                await interaction.response.edit_message(**kwargs, view=self)

    def _update_labels(self, page_number: int) -> None:
        self.go_to_first_page.disabled = page_number == 0
        if self.compact:
            max_pages = self.source.get_max_pages()
            self.go_to_last_page.disabled = max_pages is None or (page_number + 1) >= max_pages
            self.go_to_next_page.disabled = max_pages is not None and (page_number + 1) >= max_pages
            self.go_to_previous_page.disabled = page_number == 0
            return
        self.go_to_current_page.label = str(page_number + 1)
        self.go_to_previous_page.label = str(page_number)
        self.go_to_next_page.label = str(page_number + 2)
        self.go_to_next_page.disabled = False
        self.go_to_previous_page.disabled = False
        self.go_to_first_page.disabled = False
        max_pages = self.source.get_max_pages()
        if max_pages is not None:
            self.go_to_last_page.disabled = (page_number + 1) >= max_pages
            if (page_number + 1) >= max_pages:
                self.go_to_next_page.disabled = True
                self.go_to_next_page.label = "…"
            if page_number == 0:
                self.go_to_previous_page.disabled = True
                self.go_to_previous_page.label = "…"

    async def show_checked_page(self, interaction: discord.Interaction, page_number: int) -> None:
        max_pages = self.source.get_max_pages()
        try:
            if max_pages is None:
                # if it doesn't give us max_pages, it can't be checked
                await self.show_page(interaction, page_number)
            elif max_pages > page_number >= 0:
                await self.show_page(interaction, page_number)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id in (self.ctx.bot.owner_id, self.ctx.author.id):
            return True
        await interaction.response.send_message(
            "This pagination menu cannot be controlled by you, sorry!", ephemeral=True
        )
        return False

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)

    async def on_error(self, interaction: discord.Interaction, *_: Any) -> None:
        if interaction.response.is_done():
            await interaction.followup.send("An unknown error occurred, sorry", ephemeral=True)
        else:
            await interaction.response.send_message("An unknown error occurred, sorry", ephemeral=True)

    async def start(self, *, content: Optional[str] = None, ephemeral: bool = False) -> None:
        if self.check_embeds and not self.ctx.channel.permissions_for(self.ctx.me).embed_links:  # type: ignore
            await self.ctx.send("Bot does not have embed links permission in this channel.", ephemeral=True)
            return
        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        if content:
            kwargs.setdefault("content", content)
        self._update_labels(0)
        self.message = await self.ctx.send(**kwargs, view=self, ephemeral=ephemeral)

    @discord.ui.button(label="≪", style=discord.ButtonStyle.grey)
    async def go_to_first_page(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.show_page(interaction, 0)

    @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple)
    async def go_to_previous_page(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.show_checked_page(interaction, self.current_page - 1)

    @discord.ui.button(label="Current", style=discord.ButtonStyle.grey, disabled=True)
    async def go_to_current_page(self, _: discord.Interaction, __: discord.ui.Button) -> None:
        pass

    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple)
    async def go_to_next_page(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await self.show_checked_page(interaction, self.current_page + 1)

    @discord.ui.button(label="≫", style=discord.ButtonStyle.grey)
    async def go_to_last_page(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        # The call here is safe because it's guarded by `_update_labels`
        await self.show_checked_page(interaction, self.source.get_max_pages() - 1)  # type: ignore

    @discord.ui.button(label="Skip to page...", style=discord.ButtonStyle.grey)
    async def numbered_page(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        if self.message is None:
            return
        modal = NumberedPageModal(self.source.get_max_pages())
        await interaction.response.send_modal(modal)
        timed_out = await modal.wait()
        if timed_out:
            await interaction.followup.send("Took too long", ephemeral=True)
            return
        elif self.is_finished():
            await modal.interaction.response.send_message("Took too long", ephemeral=True)
            return
        value = str(modal.page.value)
        if not value.isdigit():
            await modal.interaction.response.send_message(f"Expected a number, not {value!r}", ephemeral=True)
            return
        value = int(value)
        await self.show_checked_page(modal.interaction, value - 1)
        if not modal.interaction.response.is_done():
            error = modal.page.placeholder.replace("Enter", "Expected")  # type: ignore # Can't be None
            await modal.interaction.response.send_message(error, ephemeral=True)

    @discord.ui.button(label="Quit", style=discord.ButtonStyle.red)
    async def stop_pages(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()


class ListPageSource(PageSource[T]):
    def __init__(self, entries: list[T], *, per_page: int) -> None:
        self.entries = entries
        self.per_page = per_page
        pages, left_over = divmod(len(entries), per_page)
        if left_over:
            pages += 1
        self._max_pages = pages

    def is_paginating(self) -> bool:
        return len(self.entries) > self.per_page

    def get_max_pages(self) -> int:
        return self._max_pages

    @overload
    async def get_page(self, page_number: Literal[1]) -> T:
        ...

    @overload
    async def get_page(self, page_number: int) -> list[T]:
        ...

    async def get_page(self, page_number: int) -> T | list[T]:
        if self.per_page == 1:
            return self.entries[page_number]
        else:
            base = page_number * self.per_page
            return self.entries[base : base + self.per_page]


class FieldPageSource(ListPageSource[tuple[str, str]]):
    def __init__(
        self,
        entries: list[tuple[str, str]],
        *,
        per_page: int = 12,
        inline: bool = False,
        clear_description: bool = True,
    ) -> None:
        super().__init__(entries, per_page=per_page)
        self.embed = discord.Embed(colour=discord.Colour.blurple())
        self.clear_description = clear_description
        self.inline = inline

    async def format_page(self, menu: BotPages, entries: list[tuple[str, str]]) -> discord.Embed:
        self.embed.clear_fields()
        if self.clear_description:
            self.embed.description = None
        for key, value in entries:
            self.embed.add_field(name=key, value=value, inline=self.inline)
        maximum = self.get_max_pages()
        if maximum > 1:
            text = f"Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)"
            self.embed.set_footer(text=text)
        return self.embed


class TextPageSource(ListPageSource[str]):
    def __init__(self, text: str, *, prefix: str = "```", suffix: str = "```", max_size: int = 2000) -> None:
        pages = commands.Paginator(prefix=prefix, suffix=suffix, max_size=max_size - 200)
        for line in text.split("\n"):
            pages.add_line(line)
        super().__init__(pages.pages, per_page=1)

    async def format_page(self, menu: BotPages, page: str) -> str:
        maximum = self.get_max_pages()
        if maximum > 1:
            return f"{page}\nPage {menu.current_page + 1}/{maximum}"
        return page


class SimplePageSource(ListPageSource[T]):
    async def format_page(self, menu: SimplePages, entries: list[T]) -> discord.Embed:
        pages = []
        for index, entry in enumerate(entries, start=menu.current_page * self.per_page):
            pages.append(f"{index + 1}. {entry}")
        maximum = self.get_max_pages()
        if maximum > 1:
            footer = f"Page {menu.current_page + 1}/{maximum} ({len(self.entries)} entries)"
            menu.embed.set_footer(text=footer)
        menu.embed.description = "\n".join(pages)
        return menu.embed


class SimplePages(BotPages[T]):
    def __init__(self, entries: list[T], *, ctx: Context, per_page: int = 12) -> None:
        super().__init__(SimplePageSource(entries, per_page=per_page), ctx=ctx)
        self.embed = discord.Embed(colour=discord.Colour.blurple())
