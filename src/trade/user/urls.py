from django.conf.urls import url
from .views import UserView

user_urls = [
    url(r'^$', UserView.as_view()),
]
