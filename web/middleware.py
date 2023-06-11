import logging
import os
import traceback

import aiohttp.web

from .errors import JSONException
from .types import Request, Handler, Response


log = logging.getLogger(__name__)


@aiohttp.web.middleware
async def exception_middleware(request: Request, handler: Handler) -> Response:
    try:
        response = await handler(request)
    except Exception as e:
        if isinstance(e, JSONException):
            raise e
        elif isinstance(e, aiohttp.web.HTTPException):
            raise JSONException(e)
        else:
            log.exception('In: %s %s (%s)', request.method, request.path, request.query_string, exc_info=e)
            raise JSONException(aiohttp.web.HTTPInternalServerError, message=traceback.format_exception(e)[-1].strip())
    return response


@aiohttp.web.middleware
async def auth_middleware(request: Request, handler: Handler) -> Response:
    token = request.headers.get('Authorization')
    if token is None:
        raise JSONException(aiohttp.web.HTTPUnauthorized, message='Missing Authorization header')
    if token != os.environ['BACKEND_AUTH_TOKEN']:
        raise JSONException(aiohttp.web.HTTPForbidden, message='Invalid Authorization header')
    return await handler(request)
