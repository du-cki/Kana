from starlette.requests import Request
from starlette.responses import JSONResponse

async def ping(request: Request) -> JSONResponse:
    return JSONResponse({
            "ping": "pong"
        })
