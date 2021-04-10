from django.urls import path
from . import views

tariff_urls = [
    path(r'', views.TariffsView.as_view()),
]
