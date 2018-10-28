from django.conf.urls import url
from trade.user import views

user_urls = [
    url(r'^$', views.UserView.as_view()),
]
