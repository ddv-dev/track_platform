import os
from django.core.asgi import get_asgi_application

# 1. Сначала инициализируем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django_asgi_app = get_asgi_application()

# 2. Теперь можно импортировать остальное
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing
from chat.middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": TokenAuthMiddleware(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})