from django.urls import path
from views.order import views

order_urls = [
    path(r'', views.OrderView.as_view()),      # url如: http://localhost/order
    path(r'/notify', views.OrderNotifyView.as_view()),     # url如: http://localhost/order/notify
]
