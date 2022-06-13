import discord
from discord.ext import commands

import typing
import traceback

from .constants import DOUBLE_LEFT, LEFT, RIGHT, DOUBLE_RIGHT

class SelectPage(discord.ui.Modal, title='Select the page you want to jump to.'):
    page = discord.ui.TextInput(
        label="Page",
        placeholder="Page number",
        required=True,
        style=discord.TextStyle.short
    )

    def __init__(self, total_pages: int) -> None:
        super().__init__()
        self.total_pages = total_pages

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if self.page.value.isdigit() and (int(self.page.value) < 0 or int(self.page.value) >= self.total_pages): # type: ignore
            return await interaction.response.send_message(
                    f"Invalid Page number, there are only {self.total_pages - 1} page{'s' if self.total_pages > 1 else ''}.",
                    ephemeral=True
                )
        await interaction.response.defer()


class EmbeddedPaginator(discord.ui.View):
    """
    Dumb janky paginator i wrote for the bot.
    This is a paginator that can be used to paginate through a list of strings.

    :param ctx: The context of the command.
    :param source: The list of strings to paginate.
    :param per_page: The number of strings to display per page.
    :param timeout: The amount of time in seconds before the paginator times out.
    """

    def __init__(self, ctx: commands.Context, source: list, per_page: int = 10, *, title: str = None, timeout: int = 180) -> None: # type: ignore
        super().__init__(timeout=timeout)
        self.source: typing.List[typing.Any] = list(discord.utils.as_chunks(source, per_page))
        self.per_page = per_page
        self.title = title
        self.ctx = ctx
        self.current_page = 0

    def build_embed(self, page: int) -> discord.Embed:
        return discord.Embed(
            title=self.title,
            description='\n'.join(self.source[page]),
            color=0xE59F9F
        )

    async def start(self) -> None:
        self.prettify()
        self.message = await self.ctx.send(
            embed=self.build_embed(self.current_page),
            view=self
        )

    async def jump_to(self, page: int) -> None:
        if page < 0 or page >= len(self.source):
            return None
        self.current_page = page
        self.prettify()

        self.message: discord.Message
        await self.message.edit(
            embed=self.build_embed(self.current_page),
            view=self
        )

    def prettify(self) -> None:
        self.breaker.label = f"{self.current_page + 1}/{len(self.source)}"
        if self.current_page == 0:
            self._first_page.disabled = True
            self._before.disabled = True
        else:
            self._first_page.disabled = False
            self._before.disabled = False

        if self.current_page + 1 == len(self.source):
            self._after.disabled = True
            self._last_page.disabled = True
        else:
            self._after.disabled = False
            self._last_page.disabled = False

    async def on_timeout(self) -> None:
        for children in self.children:
            children.disabled = True # type: ignore
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self.ctx.author

    @discord.ui.button(emoji=DOUBLE_LEFT, style=discord.ButtonStyle.grey)
    async def _first_page(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.defer()
        await self.jump_to(0)

    @discord.ui.button(emoji=LEFT, style=discord.ButtonStyle.grey)
    async def _before(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.defer()
        await self.jump_to(self.current_page - 1)

    @discord.ui.button(label="...", style=discord.ButtonStyle.grey)
    async def breaker(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        modal = SelectPage(len(self.source) + 1)
        await interaction.response.send_modal(modal)
        await modal.wait()

        page = modal.page.value
        if page.isdigit() and (int(page) > 0 or int(page) <= len(self.source + 1)) and int(page) - 1 != self.current_page: # type: ignore # due to the nature of the method im using this should be put here sadly
            await self.jump_to(int(page) - 1) # type: ignore

    @discord.ui.button(emoji=RIGHT, style=discord.ButtonStyle.grey)
    async def _after(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.defer()
        await self.jump_to(self.current_page + 1)

    @discord.ui.button(emoji=DOUBLE_RIGHT, style=discord.ButtonStyle.grey)
    async def _last_page(self, interaction: discord.Interaction, _: discord.ui.Button) -> None:
        await interaction.response.defer()
        await self.jump_to(len(self.source) - 1)
