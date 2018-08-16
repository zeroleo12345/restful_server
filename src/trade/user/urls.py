from django.conf.urls import url
from trade.user import views

user_urls = [
    url(r'^$', views.UserView.as_view()),
    url(r'^/resource', views.UserResourceView.as_view()),
    url(r'^/test', views.TestView.as_view()),
]
