from django.urls import path
from . import views

resource_urls = [
    path(r'', views.UserResourceView.as_view()),
]
