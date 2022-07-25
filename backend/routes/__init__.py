from starlette.routing import Route

from .get import get
from .get_raw import get_raw
from .ping import ping
from .static import static

Routes = [
    Route("/ping", ping),
    Route("/{user:int}/raw", get_raw),
    Route("/{user:int}", get),
    Route("/static/{avatar:UUID}", static),
]
