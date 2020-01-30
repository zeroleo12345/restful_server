from django.conf.urls import url
from user import views

user_urls = [
    url(r'^$', views.UserView.as_view()),
    url(r'^/sync$', views.UserSyncView.as_view()),
]
