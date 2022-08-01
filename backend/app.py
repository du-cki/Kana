from starlette.applications import Starlette

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..cogs.utils import Kana
    from asyncpg import Pool

from .routes import Routes

class App(Starlette):
    def __init__(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("on_startup", []).append(self.start)
        super().__init__(*args, **kwargs)  # type: ignore

    async def start(self) -> None:
        self.bot: Kana = self.state.bot
        self.pool: Pool[Any] = self.state.bot.pool


app = App(
    routes=Routes
)
