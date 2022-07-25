from starlette.routing import Route

from .avatars import avatars
from .ping import ping
from .static import static

Routes = [
    Route("/ping", ping),
    Route("/{user:int}/avatars", avatars),
    Route("/static/{avatar:UUID}", static),
]
