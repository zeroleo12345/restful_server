from django.conf.urls import url
from trade.order.views import OrderView, OrderNotifyView

order_urls = [
    url(r'^$', OrderView.as_view()),
    url(r'^/notify', OrderNotifyView.as_view()),
]
