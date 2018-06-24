from django.conf.urls import url
from .views import UserView

UserUrl = [
    url(r'^$', UserView.as_view()),
]
