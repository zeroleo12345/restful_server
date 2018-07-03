from django.conf.urls import url
from .views import UserView, TestView

user_urls = [
    url(r'^$', UserView.as_view()),
    url(r'^test', TestView.as_view()),
]
