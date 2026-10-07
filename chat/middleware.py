from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):

        query_string = scope["query_string"].decode()

        query_params = parse_qs(query_string)

        token = query_params.get("token", [None])[0]

        scope["user"] = AnonymousUser()

        if token:
            try:
                scope["user"] = await self.get_user(token)
            except Exception:
                pass

        return await super().__call__(
            scope,
            receive,
            send
        )

    @database_sync_to_async
    def get_user(self, token):

        jwt_auth = JWTAuthentication()

        validated_token = jwt_auth.get_validated_token(
            token
        )

        return jwt_auth.get_user(
            validated_token
        )