from django.urls import path
from views.mp import views

mp_urls = [
    path(r'/echostr', views.EchoStrView.as_view()),
]
