import asyncpg

from typing import Any

from starlette.applications import Starlette
from starlette.config import Config

from .routes import Routes

config = Config(".env")

class App(Starlette):
    def __init__(self, *args: Any, **kwargs: Any):
        kwargs.setdefault("on_startup", []).append(self.start)
        kwargs.setdefault("on_shutdown", []).append(self.close)
        super().__init__(*args, **kwargs) # type: ignore

    async def start(self) -> None:
        self.pool = await asyncpg.create_pool(dsn=config("PSQL_URI"))

    async def close(self) -> None:
        if self.pool is not None: # linter
            await self.pool.close()

app = App(
    routes=Routes
)
