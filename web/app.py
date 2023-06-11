from typing import TYPE_CHECKING
import aiohttp.web
from .middleware import exception_middleware, auth_middleware
from .the_route import post_webhook
if TYPE_CHECKING:
    from bot import IITMBot


def new_server(bot: IITMBot) -> aiohttp.web.Application:
    app = aiohttp.web.Application()
    app['bot'] = bot
    app.middlewares.append(exception_middleware)
    app.middlewares.append(auth_middleware)
    app.router.add_routes([aiohttp.web.post('/verification', post_webhook)])
    return app

