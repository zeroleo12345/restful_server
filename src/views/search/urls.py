from django.urls import path
from . import views

resource_urls = [
    path(r'', views.SearchView.as_view()),
]
