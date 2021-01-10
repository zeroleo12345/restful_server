from django.urls import path
from . import views

search_urls = [
    path(r'/user', views.SearchUserView.as_view()),
]
