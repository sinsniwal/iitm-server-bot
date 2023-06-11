import http
import json

import aiohttp.web


class JSONException(aiohttp.web.HTTPException):
    def __init__(self, exc: type[aiohttp.web.HTTPException] | aiohttp.web.HTTPException, message: str | None = None) -> None:
        body = {
            'status': exc.status_code,
            'reason': http.HTTPStatus(exc.status_code).phrase,
            'message': message,
        }
        aiohttp.web.Response.__init__(self, content_type='application/json', text=json.dumps(body))
        Exception.__init__(self)
