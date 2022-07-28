from typing import Any
from starlette.applications import Starlette

from .routes import Routes


class App(Starlette):
    def __init__(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("on_startup", []).append(self.start)
        super().__init__(*args, **kwargs)  # type: ignore

    async def start(self) -> None:
        self.pool = self.state.bot.pool


app = App(
    routes=Routes
)
