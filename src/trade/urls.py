from django.conf.urls import url, include
from user.urls import user_urls
from resource.urls import resource_urls
from order.urls import order_urls
from mp.urls import mp_urls
from heartbeat.views import HeartBeatView
from debug.views import DebugView

urlpatterns = [
    url(r'^heartbeat$', HeartBeatView.as_view()),
    url(r'^debug', DebugView.as_view()),
    url(r'^mp', include(mp_urls)),
    url(r'^user', include(user_urls)),
    url(r'^resource', include(resource_urls)),
    url(r'^order', include(order_urls)),
]
