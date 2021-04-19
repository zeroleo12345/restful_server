from django.urls import path
from trade.views.user.views import UserView, UserSyncView
from trade.views.platform.views import PlatformView
from trade.views.account.views import AccountView
from trade.views.order.views import OrderView, OrderNotifyView
from trade.views.mp.views import EchoStrView
from trade.views.search.views import SearchUserView
from trade.views.heartbeat.views import HeartBeatView
from trade.views.debug.views import DebugView

urlpatterns = [
    path(r'heartbeat', HeartBeatView.as_view()),
    path(r'debug', DebugView.as_view()),
    #
    path(r'mp/echostr', EchoStrView.as_view()),
    #
    path(r'user', UserView.as_view()),
    path(r'user/sync', UserSyncView.as_view()),
    #
    path(r'platform/<int:platform_id>', PlatformView.as_view()),
    #
    path(r'account', AccountView.as_view()),
    #
    path(r'order', OrderView.as_view()),      # url如: http://localhost/order
    path(r'order/notify', OrderNotifyView.as_view()),     # url如: http://localhost/order/notify
    #
    path(r'search/user', SearchUserView.as_view()),
]
