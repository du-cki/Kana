from starlette.requests import Request
from starlette.responses import Response

async def get(request: Request) -> Response:
    sql = '''
    SELECT avatar_id FROM avatar_history 
        WHERE user_id = $1
        ORDER BY time_changed DESC;
    '''
    query = await request.app.pool.fetch(sql, request.path_params["user"])
    if not query:
        return Response("<h1>Not Found</h1>", status_code=404)

    end = '<html><body>'
    for avatar in [query["avatar_id"] for query in query]:
        end += f'<img src="/static/{avatar}" height="100px" width="100px" style="padding: 5px;"/>'
    end += '</body></html>'

    return Response(end, media_type='text/html')
