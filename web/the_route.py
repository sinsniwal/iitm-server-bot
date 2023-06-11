import re
import aiohttp.web

from .decorators import ensure_content_type, load_json
from .errors import JSONException
from .types import Request, Response

COURSE_SPEC = re.compile(r'^\d{2}(?P<role>[a-z]+).*$')

@load_json()
@ensure_content_type('application/json')
async def post_webhook(request: Request) -> Response:
    payload = request['data']
    code = payload['code']
    if not request.app['bot'].verification:
        raise JSONException(aiohttp.web.HTTPInternalServerError, 'Verification is not enabled')
    if code == 1000:
        match = COURSE_SPEC.match(payload['email'])
        if not match:
            raise JSONException(aiohttp.web.HTTPBadRequest, 'Invalid email')
        course = match.group('role')
        await request.app['bot'].verification.verify(payload['user_id'], course)
        return aiohttp.web.Response(status=201)
    elif code == 1001: # user is already verified
        return aiohttp.web.Response(status=304)
    elif code == 1002:  # email is used by another user
        await request.app['bot'].verification.nuke_existing_user(payload['existing_user'])
        return await request.app['bot'].verification.verify(payload['user_id'])
    else:
        raise JSONException(aiohttp.web.HTTPBadRequest, 'Invalid code')
