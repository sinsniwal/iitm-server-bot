from __future__ import annotations
import os
from typing import TYPE_CHECKING, Any, Dict
from urllib.parse import urlencode
import aiohttp

import paseto
from discord.http import json_or_text
from discord.utils import MISSING, cached_property

from paseto.v4 import Ed25519PrivateKey, PublicKey

import config

if TYPE_CHECKING:
    from bot import IITMBot


class OAuth:
    def __init__(self, bot: IITMBot):
        self.bot = bot
        self._session = MISSING
    
    async def _ensure_session(self) -> None:
        if not self._session:
            self._session = aiohttp.ClientSession()
    
    @cached_property
    async def _get_openid_config(self) -> Dict[str, Any]:
        await self._ensure_session()
        async with self._session.get('https://accounts.google.com/.well-known/openid-configuration') as resp:
            return await json_or_text(resp)  # type: ignore


    async def url_for(self, user_id: int) -> str:
        openid_config = await self._get_openid_config
        payload = {'_id': user_id}
        key = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(os.environ['PASETO_PRIVATE_KEY']))
        pkey = PublicKey(key)
        bytes_ = paseto.encode(pkey, payload, exp=300)
        state = bytes_.decode('ascii')
        params = {
            'client_id': os.environ['GOOGLE_CLIENT_ID'],
            'redirect_uri': os.environ['GOOGLE_REDIRECT_URI'],
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state
        }
        auth_url = openid_config['authorization_endpoint']
        return f'{auth_url}?{urlencode(params)}'
    
    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = MISSING
