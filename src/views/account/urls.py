from django.urls import path
from . import views

account_urls = [
    path(r'', views.AccountView.as_view()),
]
