from django.conf.urls import url
from trade.order import views

order_urls = [
    url(r'^$', views.OrderView.as_view()),
    url(r'^/notify', views.OrderNotifyView.as_view()),
]
