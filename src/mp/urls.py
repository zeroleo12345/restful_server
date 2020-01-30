from django.conf.urls import url
from mp import views

mp_urls = [
    url(r'^/echostr$', views.EchoStrView.as_view()),
]
