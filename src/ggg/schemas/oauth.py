import os
from datetime import datetime, timedelta, UTC

import jwt
from authlib.integrations.starlette_client import OAuth
from fastapi import Depends
from fastapi.security import APIKeyHeader

from ggg.exception import ExpiredTokenException, InvalidTokenException

AUTHORIZATION_HEADER = APIKeyHeader(name="Authorization")

async def auth_check(token: str = Depends(AUTHORIZATION_HEADER)):
    info_from_token = AuthHandler().decode_token(token)
    return info_from_token

class AuthHandler:

    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.environ["TOKEN_ALGORITHM"]
    access_expires = timedelta(hours=1)
    refresh_expires = timedelta(days=14)

    def __new__(cls, *args, **kwargs): 
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.oauth = OAuth()

    def encode_token(self, sub: int, expires: timedelta) -> str:
        now = datetime.now(UTC)
        payload = {
            "exp": now + expires,
            "iat": now.timestamp(),
            "sub": sub,
        }

        return jwt.encode(payload, self.secret_key, self.algorithm)

    def decode_token(self, token: str, verify_exp: bool = True) -> str:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": verify_exp})
            return payload["sub"]
        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredTokenException()
        except jwt.exceptions.InvalidTokenError:
            raise InvalidTokenException()

    def create_access_token(self, user_id: int) -> str:
        return self.encode_token(sub=user_id, expires=self.access_expires)

    def create_refresh_token(self, user_id: int) -> str:
        sub = f"{user_id}.refresh"
        return self.encode_token(sub=sub, expires=self.refresh_expires)
