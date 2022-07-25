from starlette.responses import Response
from starlette.requests import Request

from ..utils import predict_media_type

# i put this as its own path for cloudflare to cache this path entirely.

async def static(request: Request) -> Response:
    avatar = request.path_params["avatar"]

    query = await request.app.pool.fetchrow("SELECT avatar, format FROM avatar_history WHERE avatar_id = $1", avatar)
    if not query:
        return Response(status_code=404)

    fmt = predict_media_type(query["format"])
    return Response(query["avatar"], media_type=fmt)
