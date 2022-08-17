from starlette.requests import Request
from starlette.responses import Response


async def avatars(request: Request) -> Response:
    userid = request.path_params["user"]
    sql = """
    SELECT avatar_id FROM avatar_history
        WHERE user_id = $1
        ORDER BY time_changed DESC;
    """
    query = await request.app.pool.fetch(sql, userid)
    if not query:
        return Response("<h1>Not Found</h1>", status_code=404)

    avatars = [query["avatar_id"] for query in query]

    og = ""
    user = request.app.state.bot.get_user(
        userid
    ) or await request.app.state.bot.fetch_user(userid)
    if user:
        og += (
            "<head>"
            f"<title>{user}'s Avatar History</title>"
            f'<link rel="icon" href="/static/{avatars[0]}">'
            '<meta property="og:type" content="website">'
            '<meta name="theme-color" content="#ffd1dc">'
            f'<meta property="og:title" content="{user}">'
            f'<meta property="og:image" content="/static/{avatars[0]}">'
            '<meta property="og:site_name" content="Discord Avatar History">'
            "</head>"
        )

    out = "<html>" + og + "<body>"
    for avatar in avatars:
        out += f'<img src="/static/{avatar}" height="200px" width="200px" style="padding: 5px;"/>'
    out += "</body></html>"

    return Response(out, media_type="text/html")