import functools
from typing import Any, Callable, NotRequired, TypedDict, overload

import aiohttp.web
import discord

from web.errors import JSONException

from .types import Handler, Request, Response

if discord.utils.HAS_ORJSON:
    from orjson import JSONDecodeError  # type: ignore
else:
    from json import JSONDecodeError

def ensure_content_type(content_type: str) -> Callable[[Handler], Handler]:
    def decorator(func: Handler) -> Handler:
        @functools.wraps(func)
        async def wrapper(request: Request) -> Response:
            if content_type != request.content_type:
                raise JSONException(aiohttp.web.HTTPBadRequest, message=f'Expected Content-Type header to be "{content_type}" but got "{request.content_type}".')
            return await func(request)
        return wrapper
    return decorator


@overload
def load_json(func: Handler) -> Handler: ...


@overload
def load_json(func: None = None) -> Callable[[Handler], Handler]: ...


def load_json(func: Handler | None = None) -> Handler | Callable[[Handler], Handler]:
    if func is None:
        return load_json
    @functools.wraps(func)
    async def wrapper(request: Request) -> Response:
        if request.can_read_body is False:
            raise JSONException(aiohttp.web.HTTPBadRequest, message='The request body must not be empty.')
        try:
            data = await discord.utils._from_json(await request.text())
        except JSONDecodeError:
            raise JSONException(aiohttp.web.HTTPBadRequest, message='The request body is not valid JSON.')
        request['data'] = data
        return await func(request)
    return wrapper
