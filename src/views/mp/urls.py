from django.urls import path
from . import views

mp_urls = [
    path(r'/echostr', views.EchoStrView.as_view()),
]
