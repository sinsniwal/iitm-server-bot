from typing import Awaitable, Callable

import aiohttp.web

Request = aiohttp.web.Request
Response = aiohttp.web.Response
Handler = Callable[[Request], Awaitable[aiohttp.web.StreamResponse]]
