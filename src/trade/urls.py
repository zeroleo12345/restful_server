from django.urls import path, include
from views.user.urls import user_urls
from views.platform.urls import platform_urls
from views.resource.urls import resource_urls
from views.order.urls import order_urls
from views.mp.urls import mp_urls
from views.search.urls import search_urls
from views.ping.views import PingView
from views.debug.views import DebugView

urlpatterns = [
    path(r'ping', PingView.as_view()),
    path(r'debug', DebugView.as_view()),
    path(r'mp', include(mp_urls)),
    path(r'user', include(user_urls)),
    path(r'platform', include(platform_urls)),
    path(r'resource', include(resource_urls)),
    path(r'order', include(order_urls)),
    path(r'search', include(search_urls)),
]
