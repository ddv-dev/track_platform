from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        # Ленивый импорт, чтобы избежать AppRegistryNotReady
        from rest_framework_simplejwt.tokens import AccessToken
        from accounts.models import User

        @database_sync_to_async
        def get_user(token_key):
            try:
                token = AccessToken(token_key)
                user_id = token.payload.get('user_id')
                return User.objects.get(id=user_id)
            except Exception:
                return AnonymousUser()

        query_string = scope['query_string'].decode()
        token = None
        for param in query_string.split('&'):
            if param.startswith('token='):
                token = param.split('=')[1]
                break
        scope['user'] = await get_user(token) if token else AnonymousUser()
        return await super().__call__(scope, receive, send)