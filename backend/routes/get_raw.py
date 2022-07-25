from starlette.requests import Request
from starlette.responses import JSONResponse, Response

async def get_raw(request: Request) -> Response | JSONResponse:
    sql = '''
    SELECT avatar_id FROM avatar_history 
        WHERE user_id = $1
        ORDER BY time_changed DESC;
    '''
    query = await request.app.pool.fetch(sql, request.path_params["user"])
    if not query:
        return Response(status_code=404)

    return JSONResponse({"avatars": [str(query["avatar_id"]) for query in query]})
