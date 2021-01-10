from django.urls import path
from . import views

search_urls = [
    path(r'', views.SearchView.as_view()),
]
